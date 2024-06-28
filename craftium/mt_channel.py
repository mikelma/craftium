import socket
import struct
import time
from typing import Optional

import numpy as np

MT_DEFAULT_PORT = 55555

class MtChannel():
    def __init__(self, img_width: int, img_height: int, port: Optional[int] = None, connect_timeout: int = 30):
        self.img_width = img_width
        self.img_height = img_height

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(30)  # time limit in seconds for minetest to connect to the socket
        self.s.bind(("127.0.0.1", MT_DEFAULT_PORT if port is None else port))

        # initialized in `reset_connection`
        self.conn = None

        # pre-compute the number of bytes that we should receive from MT.
        # the RGB image + 8 bytes of the reward + 1 byte of the termination flag
        self.rec_bytes = img_width*img_height*3 + 8 + 1

    def receive(self):
        data = []
        while len(data) < self.rec_bytes:
            data += self.conn.recv(self.rec_bytes)
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

        self.conn.sendall(bytes(keys + mouse))

    def close(self):
        if self.conn is not None:
            self.conn.close()
        self.s.close()

    def close_conn(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def open_conn(self):
        self.close_conn()
        self.s.listen()
        self.conn, addr = self.s.accept()
