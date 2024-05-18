import polars as pl
from known_ips import known_ips
from geopy.geocoders import Nominatim, Photon,GoogleV3


def get_geographical_distribution(ip):
    for item in known_ips:
        if item["ip"] == ip:
            geolocator = Nominatim(
                user_agent="measurements"
            )  
            location_data = geolocator.geocode({"city": item["location"], "country": "USA"})
            if location_data:
                latitude = location_data.latitude
                longitude = location_data.longitude
                return latitude, longitude, item["location"]
            else:
                return 0, 0, 0
    return 0, 0, 0


def get_users_distribution(files):
    user = pl.DataFrame(schema={"IP": str, "Timestamp": str})
    for file in files:
        df = pl.read_csv(file)
        user.extend(df)
    most_users = user.group_by("IP").len().sort("len", descending=True)
    col_a, col_l, col_g = zip(*map(get_geographical_distribution, most_users["IP"].to_list()))
    most_users = most_users.with_columns(
        percentil=pl.col("len") / most_users["len"].sum(),
    )
    most_users.insert_column(3,pl.Series(name="latitude",values=[*col_a]))
    most_users.insert_column(4,pl.Series(name="longitude",values=[*col_l]))
    most_users.insert_column(5,pl.Series(name="location",values=[*col_g]),)
    return most_users.to_pandas(), most_users["len"].sum()
