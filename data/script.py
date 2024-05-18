import csv
import random
from datetime import datetime, timedelta


def generate_resource_usage_data(start_time, end_time, interval_minutes):
    headers = [
        "Timestamp",
        "CPU",
        "RAM",
        "Network_Usage(Mbps)",
        "GPU",
        "Status",
    ]
    data = []

    current_time = start_time
    while current_time <= end_time:
        cpu_usage = random.randint(1, 100) / 100
        memory_consumption = (
            round(random.uniform(1, 8), 1) / 10
        )  # Random memory consumption between 1 and 8 GB
        network_usage = random.randint(1, 100) / 100
        gpu_usage = random.randint(1, 100) / 100

        # Introduce occasional resource spikes and failures
        status = "Normal"
        if random.random() < 0.005:  # 5% chance of a resource spike
            status = "Resource Spike"
            cpu_usage = random.randint(90, 100) / 100
            memory_consumption = round(random.uniform(5, 10), 1) / 10  # High memory consumption
            network_usage = random.randint(50, 100) / 100
            gpu_usage = random.randint(90, 100) / 100
        elif random.random() < 0.002:  # 2% chance of a failure
            status = "Failure"

        data.append(
            [
                current_time.strftime("%Y-%m-%d %H:%M:%S"),
                cpu_usage,
                memory_consumption,
                network_usage,
                gpu_usage,
                status,
            ]
        )
        current_time += timedelta(minutes=interval_minutes)

    return headers, data


def write_to_csv(filename, headers, data):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


def generate_fake_data(start_date, num_entries):
    data = []
    for _ in range(num_entries):
        ip_address = ".".join(["192", "168", "1", str(random.randint(1, 100))])
        access_time = start_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        data.append((ip_address, access_time))
    return data


def write_to_csv2(data, filename):
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["IP", "Timestamp"])
        csv_writer.writerows(data)


# Set start and end date for the last 3 years
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 3)

# Generate fake data

# Write data to CSV file


if __name__ == "__main__":
    data_interval = 60
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=data_interval
    )  # 2 years ago
    end_time = datetime.now()
    interval_minutes = 3

    print("generating resources data")
    headers, data = generate_resource_usage_data(start_time, end_time, interval_minutes)
    write_to_csv("data/resource_usage_data.csv", headers, data)
    del headers, data

    print("generating users data")
    for i in range(data_interval):
        fake_data = generate_fake_data(
            start_time + timedelta(days=i), random.randint(5, 36) * 60 * 60 * 24
        )
        write_to_csv2(fake_data, f"data/users_logs_{i}.csv")
        del fake_data
        print(i, "/", data_interval)
    print("CSV file generated successfully.")
