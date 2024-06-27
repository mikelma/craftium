from argparse import ArgumentParser
from uuid import uuid4
import os
from stable_baselines3 import A2C, PPO
from stable_baselines3.common import logger
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
import gymnasium as gym
import craftium

def parse_args():
    parser = ArgumentParser()

    # fmt: off
    parser.add_argument("--run-name", type=str, default=None,
        help="Unique name for the run. Defaults to a random uuid.")
    parser.add_argument("--runs-dir", type=str, default="./run-logs/",
        help="Name of the directory where run's data is stored. Defaults to './run-logs/'")

    parser.add_argument("--env-id", type=str, default="Craftium/ChopTree-v0",
        help="Name (registered) of the environment.")
    parser.add_argument("--total-timesteps", type=int, default=100_000,
        help="Number of timesteps to train for.")
    parser.add_argument("--num-envs", type=int, default=1,
        help="Number of environments to use.")
    parser.add_argument("--method", type=str, default="a2c", choices=["ppo", "a2c"],
        help="RL method to use to optimize the agent.")
    # fmt: on

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    run_name = str(uuid4()) if args.run_name is None else args.run_name
    log_path = os.path.join(args.runs_dir, run_name)

    print(f"** Storing run's data in {log_path}")
    new_logger = logger.configure(log_path, ["stdout", "csv"])

    envs = DummyVecEnv([lambda: gym.make(args.env_id) for _ in range(args.num_envs)])
    envs = VecMonitor(envs)

    method_class = PPO if args.method == "ppo" else A2C
    model = method_class("CnnPolicy", envs, verbose=1)
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.total_timesteps)

    envs.close()
