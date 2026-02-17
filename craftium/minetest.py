import os
from pathlib import Path
from typing import Optional, Any
import subprocess
from uuid import uuid4
import shutil
import random


def is_minetest_build_dir(path: os.PathLike) -> bool:
    # list of directories required by craftium to exist in the a minetest build directory
    req_dirs = ["builtin", "fonts", "locale", "textures", "bin", "client"]
    for rd in req_dirs:
        if not os.path.exists(os.path.join(path, rd)):
            return False
    return True


def is_inside_python_pkg():
    return "site-packages" in __file__


class Minetest():
    def __init__(
            self,
            tcp_port: int,
            run_dir: Optional[os.PathLike] = None,
            run_dir_prefix: Optional[os.PathLike] = None,
            headless: bool = False,
            gpu_id: Optional[int] = None,
            seed: Optional[int] = None,
            game_id: str = "minetest",
            world_name: str = "world",
            sync_dir: Optional[os.PathLike] = None,
            screen_w: int = 640,
            screen_h: int = 360,
            voxel_obs: bool = False,
            voxel_obs_rx: int = 20,
            voxel_obs_ry: int = 10,
            voxel_obs_rz: int = 20,
            minetest_dir: Optional[str] = None,
            minetest_conf: dict[str, Any] = dict(),
            pipe_proc: bool = True,
            mt_port: Optional[int] = None,
            frameskip: int = 1,
            rgb_frames: bool = True,
            sync_mode: bool = False,
            fps_max: int = 200,
            pmul: int = 1,
    ):
        self.pipe_proc = pipe_proc


        # create a dedicated directory for this run
        if run_dir is None:
            if is_inside_python_pkg():
                # NOTE: We have to nest the run dir in three subdirectories as the luanti binary
                # (patched by auditwheel when creating the python wheel) is patched to expect the
                # dynamic libs in the directory `../../../craftium.libs`.
                # Also see: `self._create_mt_dirs(...)`.
                self.run_dir = f"luanti-run-{uuid4()}/luanti/a"
            else:
                self.run_dir = f"luanti-run-{uuid4()}"
            if run_dir_prefix is not None:
                self.run_dir = os.path.join(run_dir_prefix, self.run_dir)
        else:
            self.run_dir = run_dir
        # delete the directory if it already exists
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)
        os.makedirs(self.run_dir)

        ppath = Path(self.run_dir) if not is_inside_python_pkg() else Path(self.run_dir).parent.parent
        print(f"==> Creating Luanti run directory at {ppath}")

        port = mt_port if mt_port is not None else random.randint(49152, 65535)

        config = dict(
            # Base config
            enable_sound=False,
            show_debug=False,
            enable_client_modding=True,
            csm_restriction_flags=0,
            enable_mod_channels=True,
            screen_w=screen_w,
            screen_h=screen_h,
            voxel_obs=voxel_obs,
            voxel_obs_rx=voxel_obs_rx,
            voxel_obs_ry=voxel_obs_ry,
            voxel_obs_rz=voxel_obs_rz,
            vsync=False,
            fps_max=fps_max,
            fps_max_unfocused=fps_max,
            undersampling=1,
            # fov=self.fov_y,

            craftium_port=tcp_port,
            frameskip=frameskip,
            rgb_frames=rgb_frames,

            # port used for MT's internal client<->server comm.
            port=port,
            remote_port=port,

            sync_env_mode=sync_mode,

            # Adapt HUD size to display size, based on (1024, 600) default
            # hud_scaling=self.display_size[0] / 1024,

            # Physics
            movement_acceleration_default=3.0*pmul,
            movement_acceleration_air=2.0*pmul,
            movement_acceleration_fast=10.0*pmul,
            movement_speed_walk=4.0*pmul,
            movement_speed_crouch=1.35*pmul,
            movement_speed_fast=20.0*pmul,
            movement_speed_climb=3.0*pmul,

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

        # overwrite config settings with those set via minetest_conf
        for key, value in minetest_conf.items():
            config[key] = value

        if seed is not None:
            config["fixed_map_seed"] = seed

        self._write_config(config, os.path.join(self.run_dir, "minetest.conf"))
        self.config = config

        # get the craftium's root directory, the place where all the data
        # needed by craftium's is located
        if minetest_dir is None:
            # check if the current directory is a minetest build directory
            if is_minetest_build_dir(os.getcwd()):
                root_path = os.getcwd()
            else:  # in this case, this module might be running as an installed python package
                # get the path location of the parent of this module
                root_path = os.path.join(os.path.dirname(__file__), "luanti")
        else:
            root_path = minetest_dir

        # create the directory tree structure needed by minetest
        self._create_mt_dirs(root_dir=root_path,
                             target_dir=self.run_dir, sync_dir=sync_dir)

        # compose the launch command
        self.launch_cmd = [
            "./bin/luanti",
            "--go",  # Disable main menu, directly start the game
            "--gameid", game_id,  # Select the game ID
            "--worldname", world_name,
        ]

        self.proc = None  # holds mintest's process
        self.stderr, self.stdout = None, None

        if headless:
            self.proc_env = {"SDL_VIDEODRIVER": "offscreen"}
            # If a GPU id was passed, set this environment variable to tell SDL to render using that GPU.
            # Different env variables might need to be set on different systems. 
            if gpu_id is not None:
                print(f"==> Setting Luanti to render on GPU {gpu_id} by setting SDL_HINT_EGL_DEVICE={gpu_id}")
                self.proc_env["SDL_HINT_EGL_DEVICE"] = f"{gpu_id}"
        else:
            self.proc_env = None

    def start_process(self):
        if self.pipe_proc:
            # open files for piping stderr and stdout into
            self.stderr = open(os.path.join(self.run_dir, "stderr.txt"), "a")
            self.stdout = open(os.path.join(self.run_dir, "stdout.txt"), "a")

            kwargs = dict(
                stderr=self.stderr,
                stdout=self.stdout,
            )
        else:
            kwargs = dict()

        self.proc = subprocess.Popen(
            self.launch_cmd,
            start_new_session=True,
            cwd=self.run_dir,
            env=self.proc_env,
            **kwargs,
        )

    def wait_close(self):
        if self.proc is not None:
            self.proc.wait()

    def close_pipes(self):
        # close the files where the process is being piped
        # into berfore the process itself
        if self.stderr is not None:
            self.stderr.close()
        if self.stdout is not None:
            self.stdout.close()

    def clear(self):
        run_dir = Path(self.run_dir)
        # delete the run's directory
        dir = run_dir if not is_inside_python_pkg() else run_dir.parent.parent
        if os.path.exists(dir):
            shutil.rmtree(dir)

    def overwrite_config(self, new_partial_config: dict[str, Any]):
        for key, value in new_partial_config.items():
            self.config[key] = value
        self._write_config(self.config, os.path.join(
            self.run_dir, "minetest.conf"))

    def _write_config(self, config: dict[str, Any], path: os.PathLike):
        with open(path, "w") as f:
            for key, value in config.items():
                if isinstance(value, dict):
                    for kkey, vvalue in value.items():
                        f.write(f"{key}.{kkey} = {vvalue}\n")
                else:
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

        if is_inside_python_pkg():
            craftium_dir = os.path.split(__file__)[0]
            os.symlink(os.path.join(craftium_dir, "../craftium.libs"),
                       os.path.join(target_dir, "../../craftium.libs"))

        copy_dir("bin")
        copy_dir("client")

        if sync_dir is not None:
            for item in os.listdir(sync_dir):
                src = os.path.join(sync_dir, item)
                tgt = os.path.join(target_dir, item)
                if os.path.isfile(src):  # if it's a file
                    shutil.copy(src, tgt)
                else:  # is a directory
                    shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            print(
                "* WARNING: `sync_dir` not given, copying worlds and games dirs from craftium installation dir")
            copy_dir("worlds")
            copy_dir("games")


class MTServerOnly():
    def __init__(
            self,
            run_dir_prefix: Optional[os.PathLike] = None,
            seed: Optional[int] = None,
            game_id: str = "minetest",
            world_name: str = "world",
            sync_dir: Optional[os.PathLike] = None,
            minetest_dir: Optional[str] = None,
            minetest_conf: dict[str, Any] = dict(),
            pipe_proc: bool = True,
            mt_server_port: Optional[int] = None,
            sync_mode: bool = False,
            fps_max: int = 200,
            pmul: int = 1,
    ):
        self.pipe_proc = pipe_proc

        # create a dedicated directory for this run
        self.run_dir = f"minetest-srv--{uuid4()}"
        if run_dir_prefix is not None:
            self.run_dir = os.path.join(run_dir_prefix, self.run_dir)
        # delete the directory if it already exists
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)
        os.mkdir(self.run_dir)

        print(f"==> Creating Minetest (server) run directory: {self.run_dir}")

        self.server_port = mt_server_port if mt_server_port is not None else random.randint(
            49152, 65535)

        config = dict(
            # Base config
            enable_sound=False,
            show_debug=False,
            enable_client_modding=True,
            csm_restriction_flags=0,
            enable_mod_channels=True,
            vsync=False,
            fps_max=fps_max,
            fps_max_unfocused=fps_max,
            undersampling=1,
            # fov=self.fov_y,

            # port used for MT's internal client<->server comm.
            port=self.server_port,
            remote_port=self.server_port,

            sync_env_mode=sync_mode,

            # Physics
            movement_acceleration_default=3.0*pmul,
            movement_acceleration_air=2.0*pmul,
            movement_acceleration_fast=10.0*pmul,
            movement_speed_walk=4.0*pmul,
            movement_speed_crouch=1.35*pmul,
            movement_speed_fast=20.0*pmul,
            movement_speed_climb=3.0*pmul,

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
        # overwrite config settings with those set via minetest_conf
        for key, value in minetest_conf.items():
            config[key] = value

        if seed is not None:
            config["fixed_map_seed"] = seed

        self._write_config(config, os.path.join(self.run_dir, "minetest.conf"))
        self.config = config

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

        # create the directory tree structure needed by minetest
        self._create_mt_dirs(root_dir=root_path,
                             target_dir=self.run_dir, sync_dir=sync_dir)

        # compose the launch command
        self.launch_cmd = [
            "./bin/minetest",
            "--server",  # Disable main menu, directly start the game
            "--gameid", game_id,  # Select the game ID
            "--worldname", world_name,
        ]

        self.proc = None  # holds mintest's process
        self.stderr, self.stdout = None, None

        self.proc_env = {"SDL_VIDEODRIVER": "offscreen"}

    def start_process(self):
        if self.pipe_proc:
            # open files for piping stderr and stdout into
            self.stderr = open(os.path.join(self.run_dir, "stderr.txt"), "a")
            self.stdout = open(os.path.join(self.run_dir, "stdout.txt"), "a")

            kwargs = dict(
                stderr=self.stderr,
                stdout=self.stdout,
            )
        else:
            kwargs = dict()

        self.proc = subprocess.Popen(
            self.launch_cmd,
            start_new_session=True,
            cwd=self.run_dir,
            env=self.proc_env,
            **kwargs,
        )

    def wait_close(self):
        if self.proc is not None:
            self.proc.wait()

    def close_pipes(self):
        # close the files where the process is being piped
        # into berfore the process itself
        if self.stderr is not None:
            self.stderr.close()
        if self.stdout is not None:
            self.stdout.close()

    def clear(self):
        # delete the run's directory
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)

    def overwrite_config(self, new_partial_config: dict[str, Any]):
        for key, value in new_partial_config.items():
            self.config[key] = value
        self._write_config(self.config, os.path.join(
            self.run_dir, "minetest.conf"))

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
                else:  # is a directory
                    shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            print(
                "* WARNING: `sync_dir` not given, copying worlds and games dirs from craftium installation dir")
            copy_dir("worlds")
            copy_dir("games")


class MTClientOnly():
    def __init__(
            self,
            tcp_port: int,
            client_name: str,
            mt_server_port: int = 30_000,  # NOTE 30000 is the default server port in MT
            run_dir_prefix: Optional[os.PathLike] = None,
            headless: bool = False,
            seed: Optional[int] = None,
            sync_dir: Optional[os.PathLike] = None,
            screen_w: int = 640,
            screen_h: int = 360,
            voxel_obs: bool = False,
            voxel_obs_rx: int = 20,
            voxel_obs_ry: int = 10,
            voxel_obs_rz: int = 20,
            minetest_dir: Optional[str] = None,
            minetest_conf: dict[str, Any] = dict(),
            pipe_proc: bool = True,
            frameskip: int = 1,
            rgb_frames: bool = True,
            sync_mode: bool = False,
            fps_max: int = 200,
            pmul: int = 1,
    ):
        self.pipe_proc = pipe_proc

        # create a dedicated directory for this run
        self.run_dir = f"./minetest-{client_name}-{uuid4()}"
        if run_dir_prefix is not None:
            self.run_dir = os.path.join(run_dir_prefix, self.run_dir)
        # delete the directory if it already exists
        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir)
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
            voxel_obs=voxel_obs,
            voxel_obs_rx=voxel_obs_rx,
            voxel_obs_ry=voxel_obs_ry,
            voxel_obs_rz=voxel_obs_rz,
            vsync=False,
            fps_max=fps_max,
            fps_max_unfocused=fps_max,
            undersampling=1,
            # fov=self.fov_y,

            craftium_port=tcp_port,
            frameskip=frameskip,
            rgb_frames=rgb_frames,

            # port used for MT's internal client<->server comm.
            port=mt_server_port,
            remote_port=mt_server_port,

            sync_env_mode=sync_mode,

            # Physics
            movement_acceleration_default=3.0*pmul,
            movement_acceleration_air=2.0*pmul,
            movement_acceleration_fast=10.0*pmul,
            movement_speed_walk=4.0*pmul,
            movement_speed_crouch=1.35*pmul,
            movement_speed_fast=20.0*pmul,
            movement_speed_climb=3.0*pmul,

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

        # overwrite config settings with those set via minetest_conf
        for key, value in minetest_conf.items():
            config[key] = value

        if seed is not None:
            config["fixed_map_seed"] = seed

        self._write_config(config, os.path.join(self.run_dir, "minetest.conf"))
        self.config = config

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

        # create the directory tree structure needed by minetest
        self._create_mt_dirs(root_dir=root_path,
                             target_dir=self.run_dir, sync_dir=sync_dir)

        # compose the launch command
        self.launch_cmd = [
            "./bin/minetest",
            "--address", "127.0.0.1",
            "--port", str(mt_server_port),
            "--name", client_name,
            "--go",  # Disable main menu, directly start the game
        ]

        self.proc = None  # holds mintest's process
        self.stderr, self.stdout = None, None

        self.proc_env = {"SDL_VIDEODRIVER": "offscreen"} if headless else None

    def start_process(self):
        if self.pipe_proc:
            # open files for piping stderr and stdout into
            self.stderr = open(os.path.join(self.run_dir, "stderr.txt"), "a")
            self.stdout = open(os.path.join(self.run_dir, "stdout.txt"), "a")

            kwargs = dict(
                stderr=self.stderr,
                stdout=self.stdout,
            )
        else:
            kwargs = dict()

        self.proc = subprocess.Popen(
            self.launch_cmd,
            start_new_session=True,
            cwd=self.run_dir,
            env=self.proc_env,
            **kwargs,
        )

    def wait_close(self):
        if self.proc is not None:
            self.proc.wait()

    def close_pipes(self):
        # close the files where the process is being piped
        # into berfore the process itself
        if self.stderr is not None:
            self.stderr.close()
        if self.stdout is not None:
            self.stdout.close()

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
                else:  # is a directory
                    shutil.copytree(src, tgt, dirs_exist_ok=True)
        else:
            print(
                "* WARNING: `sync_dir` not given, copying worlds and games dirs from craftium installation dir")
            copy_dir("worlds")
            copy_dir("games")
