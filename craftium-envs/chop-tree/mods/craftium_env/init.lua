voxel_radius = {
	x = minetest.settings:get("voxel_obs_rx"),
	y = minetest.settings:get("voxel_obs_ry"),
	z = minetest.settings:get("voxel_obs_rz")
}

-- Positive reward if a tree block is dug
minetest.register_on_dignode(function(pos, node)
	if string.find(node["name"], "tree") then
		-- Give a 1.0 reward once and then reset reward to 0.0 value
		set_reward_once(1.0, 0.0)
	end
end)

-- Turn on the termination flag if the agent dies
minetest.register_on_dieplayer(function(ObjectRef, reason)
	set_termination()
end)

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
	-- set timeofday to midday
	minetest.set_timeofday(0.5)

	-- Disable HUD elements
	player:hud_set_flags({
		hotbar = false,
		crosshair = false,
		healthbar = false,
		chat = false,
	})
end)

minetest.register_globalstep(function(dtime)

	-- get the first connected player
	local player = minetest.get_connected_players()[1]

	-- if the player is not connected end here
	if player == nil then
		return nil
	end

	-- if the player is connected:
	local player_pos = player:get_pos()
	if minetest.settings:get("voxel_obs") then
		local voxel_data, voxel_light_data, voxel_param2_data = voxel_api:get_voxel_data(player_pos, voxel_radius)
		set_voxel_data(voxel_data)
		set_voxel_light_data(voxel_light_data)
		set_voxel_param2_data(voxel_param2_data)
	end

end)
