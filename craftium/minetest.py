import os
from typing import Optional, Any
import subprocess
import multiprocessing
from uuid import uuid4
import shutil
import random
# from distutils.dir_util import copy_tree


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def launch_process(cmd: str, cwd: Optional[os.PathLike] = None, env_vars: dict[str, str] = dict()):
    def launch_fn():
        # set env vars
        for key, value in env_vars.items():
            os.environ[key] = value

        # open files for piping stderr and stdout into
        stderr = open(os.path.join(cwd, "stderr.txt"), "w")
        stdout = open(os.path.join(cwd, "stdout.txt"), "w")

        subprocess.run(cmd, cwd=cwd, stderr=stderr, stdout=stdout)
    process = multiprocessing.Process(target=launch_fn, args=[])
    process.start()
    return process

def is_minetest_build_dir(path: os.PathLike) -> bool:
    # list of directories required by craftium to exist in the a minetest build directory
    req_dirs = ["builtin", "fonts", "locale", "textures", "bin", "client"]
    for rd in req_dirs:
        if not os.path.exists(os.path.join(path, rd)):
            return False
    return True


class Minetest():
    def __init__(
            self,
            run_dir: Optional[os.PathLike] = None,
            run_dir_prefix: Optional[os.PathLike] = None,
            headless: bool = False,
            seed: Optional[int] = None,
            game_id: str = "minetest",
            world_name: str = "world",
            sync_dir: Optional[os.PathLike] = None,
            screen_w: int = 640,
            screen_h: int = 360,
            minetest_dir: Optional[str] = None,
            tcp_port: Optional[int] = None,
    ):
        # create a dedicated directory for this run
        if run_dir is None:
            self.run_dir = f"./minetest-run-{uuid4()}"
            if run_dir_prefix is not None:
                self.run_dir = os.path.join(run_dir_prefix, self.run_dir)
        else:
            self.run_dir = run_dir
        # delete the directory if it already exists
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)
        # create the directory
        os.mkdir(self.run_dir)

        print(f"==> Creating Minetest run directory: {self.run_dir}")

        config = dict(
            # Base config
            enable_sound=False,
            show_debug=False,
            enable_client_modding=True,
            csm_restriction_flags=0,
            enable_mod_channels=True,
            screen_w=screen_w,
            screen_h=screen_h,
            vsync=False,
            fps_max=1000,
            fps_max_unfocused=1000,
            undersampling=1,
            # fov=self.fov_y,

            # Adapt HUD size to display size, based on (1024, 600) default
            # hud_scaling=self.display_size[0] / 1024,

            # Attempt to improve performance. Impact unclear.
            server_map_save_interval=1000000,
            profiler_print_interval=0,
            active_block_range=2,
            abm_time_budget=0.01,
            abm_interval=0.1,
            active_block_mgmt_interval=4.0,
            server_unload_unused_data_timeout=1000000,
            client_unload_unused_data_timeout=1000000,
            full_block_send_enable_min_time_from_building=0.0,
            max_block_send_distance=100,
            max_block_generate_distance=100,
            num_emerge_threads=0,
            emergequeue_limit_total=1000000,
            emergequeue_limit_diskonly=1000000,
            emergequeue_limit_generate=1000000,
        )
        if seed is not None:
            config["fixed_map_seed"] = seed

        self._write_config(config, os.path.join(self.run_dir, "minetest.conf"))

        # get the craftium's root directory, the place where all the data
        # needed by craftium's is located
        if minetest_dir is None:
            # check if the current directory is a minetest build directory
            if is_minetest_build_dir(os.getcwd()):
                root_path = os.getcwd()
            else:  # in this case, this module might be running as an installed python package
                # get the path location of the parent of this module
                root_path = os.path.dirname(__file__)
        else:
            root_path = minetest_dir

        print(f"** Craftium's root path is: {root_path}")

        # create the directory tree structure needed by minetest
        self._create_mt_dirs(root_dir=root_path, target_dir=self.run_dir, sync_dir=sync_dir)

        # compose the launch command
        self.launch_cmd = [
            "./bin/minetest",
            "--go",  # Disable main menu, directly start the game
            "--gameid", game_id,  # Select the game ID
            "--worldname", world_name,
        ]

        self.proc = None  # will hold the mintest's process

        # set the env. variables to execute mintest in headless mode
        # if headless:
        #   os.environ["SDL_VIDEODRIVER"] = "offscreen"

        self.mt_env = {}

        if headless:
            self.mt_env["SDL_VIDEODRIVER"] = "offscreen"

        if tcp_port is None:
            # select a (random) free port for the craftium <-> minetest communication
            while True:
                self.port = random.randint(49152, 65535)
                if not is_port_in_use(self.port):
                    break
        else:
            self.port = tcp_port
        self.mt_env["CRAFTIUM_PORT"] = str(self.port)

    def start_process(self):
        self.proc = launch_process(self.launch_cmd, self.run_dir, env_vars=self.mt_env)

    def kill_process(self):
        self.proc.terminate()

    def clear(self):
        # delete the run's directory
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)

    def _write_config(self, config: dict[str, Any], path: os.PathLike):
        with open(path, "w") as f:
            for key, value in config.items():
                f.write(f"{key} = {value}\n")

    def _create_mt_dirs(
            self,
            root_dir: os.PathLike,
            target_dir: os.PathLike,
            sync_dir: Optional[os.PathLike] = None
    ):
        def link_dir(name):
            os.symlink(os.path.join(root_dir, name),
                       os.path.join(target_dir, name))
        def copy_dir(name):
            shutil.copytree(os.path.join(root_dir, name),
                            os.path.join(target_dir, name),
                            dirs_exist_ok=True)

        link_dir("builtin")
        link_dir("fonts")
        link_dir("locale")
        link_dir("textures")

        copy_dir("bin")
        copy_dir("client")

        if sync_dir is not None:
            for item in os.listdir(sync_dir):
                src = os.path.join(sync_dir, item)
                tgt = os.path.join(target_dir, item)
                if os.path.isfile(item):  # if it's a file
                    shutil.copy(src, tgt)
                else: # is a directory
                    shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            print("* WARNING: `sync_dir` not given, copying worlds and games dirs from craftium installation dir")
            copy_dir("worlds")
            copy_dir("games")