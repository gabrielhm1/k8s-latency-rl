import csv


def save_to_csv(file_name, episode, avg_latency, reward,penalty,execution_time):
    file = open(file_name, "a+", newline="")  # append
    # file = open(file_name, 'w', newline='')
    with file:
        fields = ["episode", "avg_latency", "reward","penalty","execution_time"]
        writer = csv.DictWriter(file, fieldnames=fields)
        # writer.writeheader()
        writer.writerow(
            {
                "episode": episode,
                "avg_latency": float("{:.4f}".format(avg_latency)),
                "reward": float("{:.2f}".format(reward)),
                "penalty": penalty,
                "execution_time": float("{:.2f}".format(execution_time))
            }
        )

def save_space_state(path,data):
    with open(f"data/{path}/k8s_state.csv", "a") as f:
        f.write(",".join(map(str, data)) + "\n")