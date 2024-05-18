import numpy as np
import polars as pl
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error
from datetime import datetime, UTC
import requests


class ResourceUsage:
    def __init__(self, file, ram, cpu, gpu):
        self.lz_df = pl.read_csv(file)
        self.ram = ram
        self.cpu = cpu
        self.gpu = gpu
        self._set_time_diff()
        self._set_and_clean_dataframe()
        self._train()
        self._validate()

    def _set_time_diff(self):
        lim_df = self.lz_df.select(pl.col("Timestamp").head(10))["Timestamp"].str.to_datetime()
        first, last = lim_df[0], lim_df[-1]
        self.time_diff = (last - first) / (lim_df.len() - 1)

    def get_medium_value(self):
        df = self.lz_df.select(["RAM", "CPU", "GPU"])
        ram = round(1.1*self.ram*max(df["RAM"].mean(), df["RAM"].median(), df["RAM"].mode()[0]), 2)
        cpu = round(1.1*self.cpu*max(df["CPU"].mean(), df["CPU"].median(), df["CPU"].mode()[0]), 2)
        gpu = round(1.1*self.gpu*max(df["GPU"].mean(), df["GPU"].median(), df["GPU"].mode()[0]), 2)
        return ram, cpu, gpu

    def get_akash_providers(self):
        r = requests.get("https://api.cloudmos.io/v1/providers")
        ram, cpu, gpu = self.get_medium_value()
        tmp = []
        r_json = r.json()
        for a in r_json:
            if (
                a.get("isOnline")
                and a.get("isAudited")
                and a.get("activeStats").get("cpu") >= cpu * 1000
                and a.get("activeStats").get("gpu") >= gpu * 1000
                and a.get("activeStats").get("memory") >= ram * (1000 * 1000 * 1000)
            ):
                tmp.append(
                    {
                        "id": a["owner"][-8:],
                        "latitude": a["ipLat"],
                        "longitude": a["ipLon"],
                        "region": a["ipRegion"],
                        "country": a["ipCountry"],
                        "totalCpu": a["activeStats"]["cpu"] / 1000,
                        "totalGpu": a["activeStats"]["gpu"] / 1000,
                        "totalRam": a["activeStats"]["memory"] / (1000 * 1000 * 1000),
                    }
                )

        return pl.DataFrame(tmp)

    def _set_and_clean_dataframe(self):
        df = self.lz_df.filter(
            (pl.col("Status") != "Normal") & (pl.col("RAM") > 0.8)
            | (pl.col("GPU") > 0.8)
            | (pl.col("CPU") > 0.8)
        )
        df = df.with_columns(df["Timestamp"].str.to_datetime())
        self.df = df.with_columns(
            (pl.col("Timestamp") + self.time_diff).alias("end_time")
        ).select(["Timestamp", "end_time"])

    def _train(self):
        dff_y = list(map(datetime.timestamp, self.df["Timestamp"].to_list()))
        sz = int(round(0.8 * self.df.height, 0))

        # Split the data into training/testing sets
        self.dff_y_train = [[int(x)] for x in dff_y[:sz]]
        self.dff_y_test = [[int(x)] for x in dff_y[sz:]]

        # Split the targets into training/testing sets
        self.dff_x_train = [[int(x)] for x in np.arange(self.df.height)[:sz]]
        self.dff_x_test = [[int(x)] for x in np.arange(self.df.height)[sz:]]

        # Create linear regression object
        self.regr = linear_model.LinearRegression()

        # Train the model using the training sets
        self.regr.fit(self.dff_x_train, self.dff_y_train)

    def _validate(self):
        dff_y_pred = self.regr.predict(self.dff_x_test)
        # The coefficients
        print("Coefficients: \n", self.regr.coef_)
        # The mean squared error
        self.rmse = root_mean_squared_error(self.dff_y_test, dff_y_pred)
        print("Mean squared error: %.2f" % self.rmse)
        # The coefficient of determination: 1 is perfect prediction
        self.cod = r2_score(self.dff_y_test, dff_y_pred)
        print("Coefficient of determination: %.2f" % self.cod)

    def next_value(self, index=1):
        ans = [
            datetime.fromtimestamp(
                self.regr.predict([[self.df.height + index]])[0][0] - self.rmse, tz=UTC
            ),
            datetime.fromtimestamp(
                self.regr.predict([[self.df.height + index]])[0][0] + self.rmse, tz=UTC
            ),
        ]
        if ans[0] <= datetime.now(UTC):
            index += 1
            ans = self.next_value(index)
        return ans
