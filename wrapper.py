import subprocess
from threading import Thread
import socket
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import struct


def launch_minetest_thread(cmd):
    def launch_command(cmd):
        subprocess.run(cmd)

    t = Thread(target=launch_command, args=[cmd])
    t.start()


def obs_client(port, obs_dim, host="127.0.0.1"):
    obs_w, obs_h = obs_dim
    obs_bytes = obs_w*obs_h*3 + 8  # the RGB image + 8 bytes of the reward value

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # main interaction loop
        frame = 0
        while True:
            # receive the whole image's bytes
            data = []
            while len(data) < obs_bytes:
                data += s.recv(obs_bytes)

            # obtain the reward value
            reward_bytes = bytes(data[-8:]) # the last 8 bytes
            # uncpack the double (float in python) in native endianess
            reward = struct.unpack("d", bytes(reward_bytes))[0]
            print(f"Reward: {reward}")

            # obtain the observation RGB image
            data = data[:-8] # get the image data, all bytes except the last 8
            # reshape received bytes into an image
            img = np.fromiter(data, dtype=np.uint8, count=(obs_bytes-8)).reshape(obs_w, obs_h, 3)

            # plt.clf()
            # plt.imshow(np.transpose(img, (1, 0, 2)))
            # plt.pause(1e-7)

            # send actions message
            # action = list(np.random.randint(2, size=21))
            action = list(np.zeros(21, dtype=np.int8))
            # action[11] = frame == 10

            # mouse position delta
            # x, y = (obs_w // 2) - np.random.randint(obs_w), (obs_h//2) - np.random.randint(obs_h)
            # action += list(struct.pack("<h", x)) + list(struct.pack("<h", y))  # no mouse movement
            action += list(struct.pack("<h", 0)) + list(struct.pack("<h", 0))  # no mouse movement

            assert len(action) == 25, f"Action vector size is {len(action)} and must be of length 25"

            s.sendall(bytes(list(action)))
            frame += 1


if __name__ == "__main__":
    cmd = ["./bin/minetest", "--go"]
    mt_obs_server_port = 4343
    mt_start_wait_seconds = 2
    mt_headless = False
    obs_dim = [640, 360] # width, hight

    if mt_headless:
        os.environ["SDL_VIDEODRIVER"] = "offscreen"

    print("** Launching minetest...")
    launch_minetest_thread(cmd)
    print("** Minetest thread launched")

    # wait for some time until minetest loads
    time.sleep(mt_start_wait_seconds)

    print("** Starting observation client")
    obs_client(port=mt_obs_server_port, obs_dim=obs_dim)
