# This script is an adaptation of the CleanRL's `ppo_atary.py` to work with Craftium environments.
#
# Original source can be found at https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo_atari.py
# Docs can be found at https://docs.cleanrl.dev/rl-algorithms/ppo/#ppo_ataripy
import os
import random
import time
from dataclasses import dataclass
from typing import Optional

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import tyro
from torch.distributions.categorical import Categorical
from torch.utils.tensorboard import SummaryWriter

import craftium
from craftium import MarlCraftiumEnv
from craftium.wrappers import DiscreteActionWrapper

@dataclass
class Args:
    exp_name: str = os.path.basename(__file__)[: -len(".py")]
    """the name of this experiment"""
    seed: Optional[int] = None
    """seed of the experiment"""
    torch_deterministic: bool = True
    """if toggled, `torch.backends.cudnn.deterministic=False`"""
    cuda: bool = True
    """if toggled, cuda will be enabled by default"""
    track: bool = False
    """if toggled, this experiment will be tracked with Weights and Biases"""
    wandb_project_name: str = "craftium"
    """the wandb's project name"""
    wandb_entity: str = None
    """the entity (team) of wandb's project"""
    mt_wd: str = "./"
    """Directory where the Minetest working directories will be created (defaults to the current one)"""
    frameskip: int = 4
    """Number of frames to skip between observations"""
    save_agent: bool = False
    """Save the agent's model (disabled by default)"""
    save_num: int = 5
    """Number of times to save the agent's model. By default it is randomly selected in the [49152, 65535] range."""
    mt_port: int = np.random.randint(49152, 65535)
    """TCP port used by Minetest server and client communication. Multiple envs will use successive ports."""
    fps_max: int = 200
    """Target FPS to run the environment"""

    # Algorithm specific arguments
    """the id of the environment"""
    total_timesteps: int = int(1e6)
    """total timesteps of the experiments"""
    learning_rate: float = 2.5e-4
    """the learning rate of the optimizer"""
    num_envs: int = 2
    """the number of parallel game environments"""
    num_steps: int = 128
    """the number of steps to run in each environment per policy rollout"""
    anneal_lr: bool = True
    """Toggle learning rate annealing for policy and value networks"""
    gamma: float = 0.99
    """the discount factor gamma"""
    gae_lambda: float = 0.95
    """the lambda for the general advantage estimation"""
    num_minibatches: int = 4
    """the number of mini-batches"""
    update_epochs: int = 4
    """the K epochs to update the policy"""
    norm_adv: bool = True
    """Toggles advantages normalization"""
    clip_coef: float = 0.1
    """the surrogate clipping coefficient"""
    clip_vloss: bool = True
    """Toggles whether or not to use a clipped loss for the value function, as per the paper."""
    ent_coef: float = 0.01
    """coefficient of the entropy"""
    vf_coef: float = 0.5
    """coefficient of the value function"""
    max_grad_norm: float = 0.5
    """the maximum norm for the gradient clipping"""
    target_kl: float = None
    """the target KL divergence threshold"""

    # to be filled in runtime
    batch_size: int = 0
    """the batch size (computed in runtime)"""
    minibatch_size: int = 0
    """the mini-batch size (computed in runtime)"""
    num_iterations: int = 0
    """the number of iterations (computed in runtime)"""


def make_env(fps_max, frameskip, mt_port, mt_wd):
    def thunk():
        env = MarlCraftiumEnv(
            num_agents=2,
            env_dir=craftium.root_path + "/craftium-envs/multi-agent-combat",
            run_dir_prefix=mt_wd,
            mt_server_port=mt_port,
            obs_width=64,
            obs_height=64,
            frameskip=frameskip,
            max_timesteps=1000,
            rgb_observations=False,
            init_frames=200,
            sync_mode=False,
            fps_max=fps_max,
        )
        env = DiscreteActionWrapper(
            env,
            # actions=["forward", "left", "right", "jump", "dig", "mouse x+", "mouse x-", "mouse y+", "mouse y-"],
            actions=["forward", "left", "right", "jump", "dig", "mouse x+", "mouse x-"],
        )
        env = gym.wrappers.FrameStack(env, 4)

        return env

    return thunk


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class Agent(nn.Module):
    def __init__(self, env):
        super().__init__()
        self.network = nn.Sequential(
            layer_init(nn.Conv2d(4, 32, 8, stride=4)),
            nn.ReLU(),
            layer_init(nn.Conv2d(32, 64, 4, stride=2)),
            nn.ReLU(),
            layer_init(nn.Conv2d(64, 64, 3, stride=1)),
            nn.ReLU(),
            nn.Flatten(),
            layer_init(nn.Linear(1024, 512)),
            nn.ReLU(),
        )
        self.actor = layer_init(nn.Linear(512, env.action_space.n), std=0.01)
        self.critic = layer_init(nn.Linear(512, 1), std=1)

    def get_value(self, x):
        return self.critic(self.network(x / 255.0))

    def get_action_and_value(self, x, action=None):
        hidden = self.network(x / 255.0)
        logits = self.actor(hidden)
        probs = Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(), self.critic(hidden)


@torch.no_grad()
def test_agent(env, agent, device):
    # reset the environment
    obs, info = env.reset()
    obs = torch.Tensor(np.array(obs)).to(device)

    ep_ret, ep_len = 0, 0
    while True:
        # get agent's action
        agent_input = obs.permute(1, 0, 2, 3)  # new size: (num_agents, framestack, H, W)
        action, logprob, _, value = agent.get_action_and_value(agent_input)
        action = action.cpu().numpy()
        # sample the action of the second (random) player
        action[1] = env.action_space.sample()

        next_obs, reward, terminations, truncations, info = env.step(action)
        obs = torch.Tensor(np.array(next_obs)).to(device)

        ep_ret += reward[0]  # ignore the reward of teh second player
        ep_len += 1
        if sum(terminations) + sum(truncations) > 0:
            break

    return ep_ret, ep_len


if __name__ == "__main__":
    args = tyro.cli(Args)
    args.batch_size = int(args.num_envs * args.num_steps)
    args.minibatch_size = int(args.batch_size // args.num_minibatches)
    args.num_iterations = (args.total_timesteps // args.frameskip) // args.batch_size
    t = int(time.time())
    run_name = f"{args.exp_name}__{args.seed}__{t}"
    if args.seed is None:
        args.seed = t

    if args.track:
        import wandb

        wandb.init(
            project=args.wandb_project_name,
            entity=args.wandb_entity,
            sync_tensorboard=True,
            config=vars(args),
            name=run_name,
            monitor_gym=True,
            save_code=True,
        )
    writer = SummaryWriter(f"runs-marl/{run_name}")
    writer.add_text(
        "hyperparameters",
        "|param|value|\n|-|-|\n%s" % ("\n".join([f"|{key}|{value}|" for key, value in vars(args).items()])),
    )

    if args.save_agent:
        agent_path = f"agents/{run_name}"
        os.makedirs(agent_path, exist_ok=True)

    # TRY NOT TO MODIFY: seeding
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.backends.cudnn.deterministic = args.torch_deterministic

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")

    # env setup
    args.num_envs = 2  # One for each agent
    env = make_env(
        fps_max=args.fps_max,
        frameskip=args.frameskip,
        mt_port=args.mt_port,
        mt_wd=args.mt_wd
    )()

    assert isinstance(env.action_space, gym.spaces.Discrete), "only discrete action space is supported"

    agent = Agent(env).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)

    # ALGO Logic: Storage setup
    obs = torch.zeros((args.num_steps,) + env.observation_space.shape).to(device)
    actions = torch.zeros((args.num_steps, args.num_envs) + env.action_space.shape).to(device)
    logprobs = torch.zeros((args.num_steps, args.num_envs)).to(device)
    rewards = torch.zeros((args.num_steps, args.num_envs)).to(device)
    dones = torch.zeros((args.num_steps, args.num_envs)).to(device)
    values = torch.zeros((args.num_steps, args.num_envs)).to(device)

    # TRY NOT TO MODIFY: start the game
    global_step = 0
    start_time = time.time()
    next_obs, _ = env.reset(seed=args.seed)
    next_obs = torch.Tensor(np.array(next_obs)).to(device)

    # next_obs = torch.vstack([torch.Tensor(obs) for obs in obs_lst]).to(device)
    next_done = torch.zeros(args.num_envs).to(device)

    reset_in_next_step = False

    ep_rets, ep_len, num_ep = np.zeros(args.num_envs), 0, 0
    for iteration in range(1, args.num_iterations + 1):
        # Annealing the rate if instructed to do so.
        if args.anneal_lr:
            frac = 1.0 - (iteration - 1.0) / args.num_iterations
            lrnow = frac * args.learning_rate
            optimizer.param_groups[0]["lr"] = lrnow

        for step in range(0, args.num_steps):
            # reset the environment if needed
            if reset_in_next_step:
                next_obs, _ = env.reset(seed=args.seed)
                next_obs = torch.Tensor(np.array(next_obs)).to(device)
                reset_in_next_step = False

            global_step += args.num_envs * args.frameskip
            obs[step] = next_obs
            dones[step] = next_done

            # ALGO LOGIC: action logic
            with torch.no_grad():
                agent_input = next_obs.permute(1, 0, 2, 3)  # new size: (num_agents, framestack, H, W)
                action, logprob, _, value = agent.get_action_and_value(agent_input)
                values[step] = value.flatten()
            actions[step] = action
            logprobs[step] = logprob

            # TRY NOT TO MODIFY: execute the game and log data.
            next_obs, reward, terminations, truncations, info = env.step(action.cpu().numpy())

            ep_rets += reward
            ep_len += 1
            if sum(terminations) + sum(truncations) > 0:
                num_ep += 1
                print(f"global_step={global_step}, episodic_return={ep_rets}")
                writer.add_scalar("charts/episodic_return_agent0", ep_rets[0], global_step)
                writer.add_scalar("charts/episodic_return_agent1", ep_rets[1], global_step)
                writer.add_scalar("charts/episodic_length", ep_len*args.frameskip, global_step)

                if num_ep % 10 == 0:
                    test_ep_ret, test_ep_len = test_agent(env, agent, device)
                    print(f"global_step={global_step}, test_ep_ret={test_ep_ret}, test_ep_len={test_ep_len}")
                    writer.add_scalar("charts/test_ep_ret", test_ep_ret, global_step)
                    writer.add_scalar("charts/test_ep_len", test_ep_len, global_step)

                # reset episode statistic
                ep_rets, ep_len = np.zeros(args.num_envs), 0

                reset_in_next_step = True

            next_done = np.logical_or(terminations, truncations)
            rewards[step] = torch.tensor(reward).to(device).view(-1)
            next_obs, next_done = torch.Tensor(np.array(next_obs)).to(device), torch.Tensor(next_done).to(device)

        # bootstrap value if not done
        with torch.no_grad():
            agent_input = next_obs.permute(1, 0, 2, 3)  # new size: (num_agents, framestack, H, W)
            next_value = agent.get_value(agent_input).reshape(1, -1)
            advantages = torch.zeros_like(rewards).to(device)
            lastgaelam = 0
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    nextnonterminal = 1.0 - next_done
                    nextvalues = next_value
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    nextvalues = values[t + 1]
                delta = rewards[t] + args.gamma * nextvalues * nextnonterminal - values[t]
                advantages[t] = lastgaelam = delta + args.gamma * args.gae_lambda * nextnonterminal * lastgaelam
            returns = advantages + values

        # flatten the batch
        b_obs = obs.permute(0, 2, 1, 3, 4).flatten(0, 1) # new size: (batch*num_agents, framestack, H, W)
        b_logprobs = logprobs.reshape(-1)
        b_actions = actions.reshape((-1,) + env.action_space.shape)
        b_advantages = advantages.reshape(-1)
        b_returns = returns.reshape(-1)
        b_values = values.reshape(-1)

        # Optimizing the policy and value network
        b_inds = np.arange(args.batch_size)
        clipfracs = []
        for epoch in range(args.update_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, args.batch_size, args.minibatch_size):
                end = start + args.minibatch_size
                mb_inds = b_inds[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(b_obs[mb_inds], b_actions.long()[mb_inds])
                logratio = newlogprob - b_logprobs[mb_inds]
                ratio = logratio.exp()

                with torch.no_grad():
                    # calculate approx_kl http://joschu.net/blog/kl-approx.html
                    old_approx_kl = (-logratio).mean()
                    approx_kl = ((ratio - 1) - logratio).mean()
                    clipfracs += [((ratio - 1.0).abs() > args.clip_coef).float().mean().item()]

                mb_advantages = b_advantages[mb_inds]
                if args.norm_adv:
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                # Policy loss
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - args.clip_coef, 1 + args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                if args.clip_vloss:
                    v_loss_unclipped = (newvalue - b_returns[mb_inds]) ** 2
                    v_clipped = b_values[mb_inds] + torch.clamp(
                        newvalue - b_values[mb_inds],
                        -args.clip_coef,
                        args.clip_coef,
                    )
                    v_loss_clipped = (v_clipped - b_returns[mb_inds]) ** 2
                    v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                    v_loss = 0.5 * v_loss_max.mean()
                else:
                    v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()

                entropy_loss = entropy.mean()
                loss = pg_loss - args.ent_coef * entropy_loss + v_loss * args.vf_coef

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), args.max_grad_norm)
                optimizer.step()

            if args.target_kl is not None and approx_kl > args.target_kl:
                break

        y_pred, y_true = b_values.cpu().numpy(), b_returns.cpu().numpy()
        var_y = np.var(y_true)
        explained_var = np.nan if var_y == 0 else 1 - np.var(y_true - y_pred) / var_y

        # TRY NOT TO MODIFY: record rewards for plotting purposes
        writer.add_scalar("charts/learning_rate", optimizer.param_groups[0]["lr"], global_step)
        writer.add_scalar("losses/value_loss", v_loss.item(), global_step)
        writer.add_scalar("losses/policy_loss", pg_loss.item(), global_step)
        writer.add_scalar("losses/entropy", entropy_loss.item(), global_step)
        writer.add_scalar("losses/old_approx_kl", old_approx_kl.item(), global_step)
        writer.add_scalar("losses/approx_kl", approx_kl.item(), global_step)
        writer.add_scalar("losses/clipfrac", np.mean(clipfracs), global_step)
        writer.add_scalar("losses/explained_variance", explained_var, global_step)
        print("SPS:", int(global_step / (time.time() - start_time)))
        writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)

        if args.save_agent and \
           (iteration % (args.num_iterations//args.save_num) == 0 \
            or iteration == args.num_iterations):
            print("Saving agent...")
            torch.save(agent, f"{agent_path}/agent_step_{global_step}.pt")

    env.close()
    writer.close()
