import csv


def save_to_csv(file_name, episode, avg_latency, reward, execution_time):
    file = open(file_name, "a+", newline="")  # append
    # file = open(file_name, 'w', newline='')
    with file:
        fields = ["episode", "avg_latency", "reward", "execution_time"]
        writer = csv.DictWriter(file, fieldnames=fields)
        # writer.writeheader()
        writer.writerow(
            {
                "episode": episode,
                "avg_latency": float("{:.4f}".format(avg_latency)),
                "reward": float("{:.2f}".format(reward)),
                "execution_time": float("{:.2f}".format(execution_time)),
            }
        )
