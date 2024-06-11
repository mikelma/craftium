import socket
import struct

import numpy as np

MT_IP = "127.0.0.1"
MT_PORT = 4343

class MtClient():
    def __init__(self, img_width: int, img_height: int):
        self.img_width = img_width
        self.img_height = img_height

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((MT_IP, MT_PORT))

        # pre-compute the number of bytes that we should receive from MT.
        # the RGB image + 8 bytes of the reward + 1 byte of the termination flag
        self.rec_bytes = img_width*img_height*3 + 8 + 1

    def receive(self):
        data = []
        while len(data) < self.rec_bytes:
            data += self.s.recv(self.rec_bytes)
        data = data[:self.rec_bytes]

        # reward bytes (8) + termination bytes (1)
        head = data[:-(8+1)]
        tail = data[-(8+1):]

        # decode the reward value
        reward_bytes = bytes(tail[:-1])  # first 8 bytes
        # uncpack the double (float in python) in native endianess
        reward = struct.unpack("d", bytes(reward_bytes))[0]
        # decode the termination byte
        termination = int(tail[-1]) != 0

        # decode the observation RGB image
        # reshape received bytes into an image
        img = np.fromiter(
            head,
            dtype=np.uint8,
            count=len(head),
        ).reshape(self.img_width, self.img_height, 3)

        return img, reward, termination

    def send(self, keys: list[int], mouse_x: int, mouse_y: int):
        assert len(keys) == 21, f"Keys list must be of length 21 and is {len(keys)}"

        mouse = list(struct.pack("<h", mouse_x)) + list(struct.pack("<h", mouse_y))

        self.s.sendall(bytes(keys + mouse))

    def close(self):
        self.s.close()
