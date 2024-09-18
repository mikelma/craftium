from typing import Optional
from .random_map_generator import RandomMapGen
import os
from .. import make_dungeon_env

def load_task(
        seq_name: str,
        task_id: int = 0,
        make_env: bool = True,
        return_map: bool = False,
        prefix: Optional[os.PathLike] = None,
        **kwargs):
    """Loads a task from a predefined continual RL task sequence.

    Example usage:
    ```python
    # Instantiate an environment with the third task
    env = crl.load_task("sequence01", task_id=2)

    # Get the ASCII map of the first task
    ascii_map = crl.load_task("sequence01", make_env=False, return_map=True)
    ```
    :param seq_name: Name of the sequence to load.
    :param task_id: Identifier of the task to load.
    :param make_env: If set to `True`, a `Gymnasium` environment of the task will be returned.
    :param return_map: If set to `True`, the ASCII map will be returned.
    :param prefix: Prefix path to add to `seq_name`. Defaults to the path of the module. Useful to load custom sequences.
    :param **kwargs: keyword arguments to pass to the `make_dungeon_env` function (see the [reference](reference.md)).
    """
    # open the sequence file and read all the maps
    prefix = os.path.dirname(__file__) if prefix is None else prefix
    try:
        file = open(os.path.join(prefix, seq_name), "r")
        maps = file.read().split("=")
        file.close()
    except Exception as _:
        raise Exception(f"Sequence '{seq_name}' does not exist")
    # get the map of the sequence
    assert task_id < len(maps), f"Task ID ({task_id}) must be smaller than the number of tasks {len(maps)}"
    ascii_map = maps[task_id]

    ret_vals = []  # list of values to return

    # instantiate a dungeon environment if needed
    if make_env:
        env = make_dungeon_env(ascii_map, **kwargs)
        ret_vals.append(env)

    if return_map:
        ret_vals.append(ascii_map)

    if len(ret_vals) == 1:
        return ret_vals[0]
    return tuple(ret_vals)
