import os
from typing import Optional, Any
import subprocess
import multiprocessing
from uuid import uuid4
import shutil
from distutils.dir_util import copy_tree


def launch_process(cmd: str, cwd: Optional[os.PathLike] = None):
    def launch_fn():
        stderr = open(os.path.join(cwd, "stderr.txt"), "w")
        stdout = open(os.path.join(cwd, "stdout.txt"), "w")
        subprocess.run(cmd, cwd=cwd, stderr=stderr, stdout=stdout)
    process = multiprocessing.Process(target=launch_fn, args=[])
    process.start()
    return process


class Minetest():
    def __init__(
            self,
            run_dir: Optional[os.PathLike] = None,
            run_dir_prefix: Optional[os.PathLike] = None,
            headless: bool = False,
            seed: Optional[int] = None,
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
            screen_w=640,
            screen_h=360,
            vsync=False,
            fps_max=1000,
            fps_max_unfocused=1000,
            undersampling=1,
            # fov=self.fov_y,
            # game_dir=self.game_dir,

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

        # get the path location of the parent of this module (where all the minetest stuff is located)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # create the directory tree structure needed by minetest
        self._create_mt_dirs(root_dir=root_path, target_dir=self.run_dir)

        self.launch_cmd = ["./bin/minetest", "--go"]

        # set the env. variables to execute mintest in headless mode
        if headless:
            os.environ["SDL_VIDEODRIVER"] = "offscreen"

        self.proc = None

    def start_process(self):
        self.proc = launch_process(self.launch_cmd, self.run_dir)

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

    def _create_mt_dirs(self, root_dir: os.PathLike, target_dir: os.PathLike):
        def link_dir(name):
            os.symlink(os.path.join(root_dir, name),
                       os.path.join(target_dir, name))
        def copy_dir(name):
            copy_tree(os.path.join(root_dir, name),
                      os.path.join(target_dir, name))

        link_dir("builtin")
        link_dir("fonts")
        link_dir("locale")
        link_dir("textures")

        copy_dir("bin")
        copy_dir("worlds")
        copy_dir("games")
        copy_dir("client")
