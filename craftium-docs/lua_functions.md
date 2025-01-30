# Extensions to Luanti's Lua API

Minetest has an extensive and powerful Lua API (check docs [here](https://api.minetest.net/)) that can be used to modify the behavior of the game engine and create mods or entire games. Craftium extends this API to include several functions needed to develop reinforcement learning environments (tutorial [here](./creating-envs.md)) such as the reward function and conditions for episode termination. The complete list of Lua functions added by craftium is provided below.

<br>
`set_reward(r: float)`: Sets the reward value to `r`. Note that the reward value is maintained for the following timesteps until another call to a function modifying the reward value is done.

<br>
`set_reward_once(r_now: float, r_after: float)`: Sets the reward to `r_now` for the current timestep, resetting it to `r_after` after (until a reward modification function is called).

<br>
`set_termination()`: Sets the termination flag to `True` in the current timestep.

<br>
`get_reward()`: Returns the reward value in the current timestep.

<br>
`get_termination()`: Returns `1.0` if the termination flag is set to `true` in the current timestep, otherwise `0.0`.

<br>
`reset_termination()`: Resets the termination flag (to `False`). This function is used for soft resets.

<br>
`get_soft_reset()`: Returns `1.0` if the environment has to soft reset, `0.0` otherwise. This function is used in the soft reset context to check whether the `env.reset` has been called in the python side.
