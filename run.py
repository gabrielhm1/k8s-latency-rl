from utils.logger import setup_logging
import argparse

from setuptools.command.alias import alias
from stable_baselines3 import PPO
from stable_baselines3 import A2C
from sb3_contrib import RecurrentPPO

from env import LatencyAware
from stable_baselines3.common.callbacks import CheckpointCallback

# Logging
from utils.model_test import test_model

logger = setup_logging()

parser = argparse.ArgumentParser(description="Run ILP!")
parser.add_argument(
    "--alg", default="ppo", help='The algorithm: ["ppo", "recurrent_ppo", "a2c"]'
)
parser.add_argument("--k8s", default=False, action="store_true", help="K8s mode")
parser.add_argument(
    "--goal", default="latency", help='Reward Goal: ["cost", "latency"]'
)

parser.add_argument(
    "--training", default=False, action="store_true", help="Training mode"
)
parser.add_argument(
    "--testing", default=False, action="store_true", help="Testing mode"
)
parser.add_argument(
    "--loading", default=False, action="store_true", help="Loading mode"
)
parser.add_argument(
    "--load_path",
    default="logs/model/test.zip",
    help="Loading path, ex: logs/model/test.zip",
)
parser.add_argument(
    "--test_path",
    default="logs/model/test.zip",
    help="Testing path, ex: logs/model/test.zip",
)

parser.add_argument("--name", default="test", help="The name of the test.")

parser.add_argument("--steps", default=200, help="The steps for saving.")
parser.add_argument("--total_steps", default=200000, help="The total number of steps.")

args = parser.parse_args()


def get_model(alg, env, tensorboard_log):
    model = 0
    if alg == "ppo":
        model = PPO(
            "MlpPolicy", env, verbose=1, tensorboard_log=tensorboard_log,
            n_steps=500,
        )
    elif alg == "recurrent_ppo":
        model = RecurrentPPO(
            "MlpLstmPolicy", env, verbose=1, tensorboard_log=tensorboard_log
        )
    elif alg == "a2c":
        model = A2C(
            "MlpPolicy", env, verbose=1, tensorboard_log=tensorboard_log
        )  # , n_steps=steps
    else:
        logger.info("Invalid algorithm!")

    return model


def get_load_model(alg, tensorboard_log, load_path):
    if alg == "ppo":
        return PPO.load(
            load_path,
            reset_num_timesteps=False,
            verbose=1,
            tensorboard_log=tensorboard_log,
            n_steps=500,
        )
    elif alg == "recurrent_ppo":
        return RecurrentPPO.load(
            load_path,
            reset_num_timesteps=False,
            verbose=1,
            tensorboard_log=tensorboard_log,
        )  # n_steps=steps
    elif alg == "a2c":
        return A2C.load(
            load_path,
            reset_num_timesteps=False,
            verbose=1,
            tensorboard_log=tensorboard_log,
        )
    else:
        logger.info("Invalid algorithm!")


def main():
    # Import and initialize Environment
    logger.info(args)

    alg = args.alg
    k8s = args.k8s
    goal = args.goal
    test_name = args.name
    loading = args.loading
    load_path = args.load_path
    training = args.training
    testing = args.testing
    test_path = args.test_path

    steps = int(args.steps)
    total_steps = int(args.total_steps)

    env = LatencyAware(namespace="learning", waiting_period=5, type="online",mode="test")

    scenario = ""
    if k8s:
        scenario = "real"
    else:
        scenario = "simulated"

    tensorboard_log = "results/" + "latency" + "/" + scenario + "/" + goal + "/"

    name = (
        alg
        + "_env_"
        + test_name
        + "_k8s_"
        + str(k8s)
        + "_totalSteps_"
        + str(total_steps)
    )

    # callback
    checkpoint_callback = CheckpointCallback(
        save_freq=steps, save_path="logs/" + name, name_prefix=name
    )

    if training:
        if loading:  # resume training
            logger.info(f"[INIT] | Training | Loading from: {load_path} ")
            model = get_load_model(alg, tensorboard_log, load_path)
            model.set_env(env)
            model.learn(
                total_timesteps=total_steps,
                tb_log_name=name + "_run",
                callback=checkpoint_callback,
            )
        else:
            logger.info(f"[INIT] | Training | No Load ")
            model = get_model(alg, env, tensorboard_log)
            model.learn(
                total_timesteps=total_steps,
                tb_log_name=name + "_run",
                callback=checkpoint_callback,
            )

        model.save(name)

    if testing:
        logger.info(f"[INIT] | Testing | Loading from: {test_path} ")
        model = get_load_model(alg, tensorboard_log, test_path)
        test_model(
            model,
            env,
            n_episodes=3000,
            n_steps=20,
            smoothing_window=5,
            fig_name=name + "_test_reward.png",
        )


if __name__ == "__main__":
    main()
