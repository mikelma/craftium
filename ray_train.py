from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
import gymnasium as gym
import os


def make_env(config):
    import craftium
    kwargs = config["kwargs"]
    env = gym.make(config["env_id"], **kwargs)
    env = gym.wrappers.FrameStack(env, 3) # NOTE: This isn't 4 in for Ray to detect it as an RGB image
    return env


if __name__ == "__main__":
    register_env("CraftiumEnv", make_env)

    # Configure logging directory
    log_dir = "rllib_training_logs"
    os.makedirs(log_dir, exist_ok=True)
    metrics_file = open(f"{log_dir}/training_metrics.txt", "w")
    metrics_file.write("iteration,timesteps_total,ep_rwd_max,ep_rwd_mean,ep_len_mean,env_wait_ms,loss,policy_loss,vf_loss\n")

    env_cfg = dict(
        env_id="Craftium/ChopTree-v0",
        kwargs=dict(
            frameskip=4,
            rgb_observations=False,
            gray_scale_keepdim=True,
        ),
    )

    # For all options see: https://docs.ray.io/en/latest/rllib/rllib-training.html#configuring-rllib-algorithms

    config = (  # 1. Configure the algorithm,
        PPOConfig()
        .environment("CraftiumEnv", env_config=env_cfg)
        .env_runners(num_env_runners=4)
        .framework("torch")
        # .training(model={"fcnet_hiddens": [64, 64]})
        # .evaluation(evaluation_num_env_runners=1)
    )

    algo = config.build()

    for iteration in range(2):
        result = algo.train()
        # print(result)

        timesteps_total = result["timesteps_total"]

        ep_data = result["env_runners"]
        ep_rwd_max = ep_data["episode_reward_max"]
        ep_rwd_mean = ep_data["episode_reward_mean"]
        ep_len_mean = ep_data["episode_len_mean"]
        env_wait_ms = ep_data["sampler_perf"]["mean_env_wait_ms"]

        stats = result["info"]["learner"]["default_policy"]["learner_stats"]
        loss = stats["total_loss"]
        policy_loss = stats["policy_loss"]
        vf_loss = stats["vf_loss"]

        print(f"Iteration {iteration+1}: Reward Mean: {ep_rwd_mean} - Timesteps: {timesteps_total}")
        metrics_file.write(f"{iteration+1},{timesteps_total},{ep_rwd_max},{ep_rwd_mean},{ep_len_mean},{env_wait_ms},{loss},{policy_loss},{vf_loss}\n")

    metrics_file.close()

    # Save the trained model checkpoint
    # algo.save(log_dir)
    # print(f"Checkpoint saved at {checkpoint_path}")
