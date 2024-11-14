import socket
import struct
import os
from typing import Optional
import numpy as np
import mt_server


class MtChannel():
    def __init__(
            self,
            img_width: int,
            img_height: int,
            listen_timeout: int = 2000,
            rgb_imgs: bool = True
    ):
        self.img_width = img_width
        self.img_height = img_height
        self.listen_timeout = listen_timeout

        self.port, self.sockfd = mt_server.init_server()

        # initialized in `reset_connection`
        self.connfd = None

        # pre-compute the number of bytes that we should receive from MT.
        # the RGB image + 8 bytes of the reward + 1 of the termination flag
        self.n_chan = 3 if rgb_imgs else 1
        self.rec_bytes = img_width*img_height*self.n_chan + 8 + 1

    def receive(self):
        img, reward, termination = mt_server.server_recv(
            self.connfd,
            self.rec_bytes,
            self.img_width,
            self.img_height,
            self.n_chan,
        )
        return img, reward, termination

    def send(self, keys: list[int], mouse_x: int, mouse_y: int, terminate: bool = False, kill: bool = False):
        assert len(keys) == 21, f"Keys list must be of length 21 and is {len(keys)}"

        mouse = list(struct.pack("<h", mouse_x)) + list(struct.pack("<h", mouse_y))

        b = bytes(keys + mouse + [int(terminate)] + [int(kill)])

        mt_server.server_send(self.connfd, b)

    def send_termination(self):
        self.send(keys=[0]*21, mouse_x=0, mouse_y=0, terminate=True)

    def send_kill(self):
        self.send(keys=[0]*21, mouse_x=0, mouse_y=0, kill=True)

    def is_open(self):
        return self.connfd is not None

    def close(self):
        """Close the MT connection and the listening server.
        """
        self.close_conn()
        os.close(self.sockfd)

    def close_conn(self):
        """Close the connection with MT, if it's open.
        """
        if self.is_open():
            os.close(self.connfd)
            self.connfd = None

    def open_conn(self):
        self.close_conn()
        self.connfd = mt_server.server_listen(self.sockfd, self.listen_timeout)
