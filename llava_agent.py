# NOTE: This script requires an active ollama server.
#       See: https://github.com/ollama/ollama

import gymnasium as gym
import craftium
from argparse import ArgumentParser
import ollama
from PIL import Image
import io
import time
import os
from uuid import uuid4


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("--frames", type=str, default="frames")
    parser.add_argument("--train-mins", type=int, default=60)
    parser.add_argument("--log", type=str, default="llm_agent_"+str(uuid4())+".csv")

    return parser.parse_args()

def obs_to_bytes(observation):
    """Converts an observation encoded as a numpy array into a bytes representation of a PNG image."""
    image = Image.fromarray(observation)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    image_binary_data = image_bytes.read()
    return image_binary_data, image


if __name__ == "__main__":
    args = parse_args()

    config = dict(
        max_block_generate_distance=3, # 16x3 blocks
        # hud_scaling=0.9,
        fov=90,
        console_alpha=0,
        smooth_lighting=False,
        performance_tradeoffs=True,
        enable_particles=False,
    )

    env = gym.make(
        "Craftium/OpenWorld-v0",
        frameskip=1,
        obs_width=520,
        obs_height=520,
        # render_mode="human",
        # pipe_proc=False,
        minetest_conf=config,
    )

    observation, info = env.reset()

    act_names = [
        "do nothing", "move forward", "move backward", "move left", "move right",
        "jump", "sneak", "use tool", "place",
        "select hotbar slot 1", "select hotbar slot 2", "select hotbar slot 3", "select hotbar slot 4", "select hotbar slot 5",
        "move camera right", "move camera left", "move camera up", "move camera down"]

    objectives = ["is to chop a tree", "is to collect stone", "is to collect iron", "is to find diamond blocks"]
    obj_rwds = [128, 256, 1024, 2048]
    objective_id = 0

    start = time.time()
    ep_ret = 0
    t_step = 0
    episode = 0
    while (time.time() - start) / 60 < args.train_mins:
        img_bytes, img = obs_to_bytes(observation)
        img.save(os.path.join(args.frames, f"frame_{str(t_step).zfill(7)}.png"), "PNG")

        prompt = f"You are a reinforcement learning agent in the Minecraft game. You will be presented the current observation, and you have to select the next action with the ultimate objective to fulfill your goal. In this case, the goal {objectives[objective_id]}. You should fight monsters and hunt animals just as a secondary objective and survival. Available actions are: do nothing, move forward, move backward, move left, move right, jump, sneak, use tool, place, select hotbar slot 1, select hotbar slot 2, select hotbar slot 3, select hotbar slot 4, select hotbar slot 5, move camera right, move camera left, move camera up, move camera down. From now on, your responses must only contain the name of the action you will take, nothing else."
        print("Prompt:", prompt)

        response = ollama.generate("llava", prompt, images=[img_bytes])
        content = response["response"]
        print("Response:", '"' + content + '"')

        # parse the next action from the reponse of the agent
        act_str = content.strip().lower().replace(".", "")
        incorrect = False
        candidates = [i for i, name in enumerate(act_names) if name in act_str]
        print(candidates)
        if len(candidates) == 0: # if the response is in an incorrect format
            action = env.action_space.sample()  # take a random action
            incorrect = True
            print("[WARNING] Incorrect action. Using random action.")
        else:
            action = candidates[0]
            if len(candidates) > 1:
                print("[WARNING] More than one action candidate detected.")

        print(f"* Action: {action}")

        if act_names[action] == "jump":
            _, _, _, _, _ = env.step(action)
            observation, reward, terminated, truncated, _info = env.step(1)
        else:
            observation, reward, terminated, truncated, _info = env.step(action)

        ep_ret += reward
        print(f"Step: {t_step}, Elapsed: {int(time.time()-start)}s, Reward: {reward}, Ep. ret.: {ep_ret}")

        # check if a stage has been completed
        if reward >= 128.0:
            objective_id += 1
            if objective_id == len(objectives):
                print("\n[!!] All objectives completed!\n")
                break
            print("\n[STAGE] Stage completed! The new objective {}\n")

        with open(args.log, "a" if t_step > 0 else "w") as f:
            if t_step == 0:
                f.write("t_step,episode,elapsed mins,reward,ep_ret,objective_id,id\n")
            f.write(f"{t_step},{episode},{(time.time()-start)/60},{reward},{ep_ret},{objective_id},{args.log}\n")

        if terminated or truncated:
            episode += 1
            observation, info = env.reset()
            ep_ret = 0
            objective_id = 0
        print()
        t_step += 1

    env.close()
