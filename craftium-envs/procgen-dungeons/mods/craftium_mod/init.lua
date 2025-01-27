rwd_objective = minetest.settings:get("rwd_objective")
rwd_kill_monster = minetest.settings:get("rwd_kill_monster")

objective_pos = nil
player_pos = nil
mobs_info = {}
spawned_mobs = {}

-- Spawn a monster of the given name in a position, disabling the infotext of the monster
spawn_monster = function(pos, name)
	local obj = minetest.add_entity(pos, name)

	-- Get the registered monster object
	local mob_def = minetest.registered_entities[name]
	if mob_def then
		-- Remove the update_tag function, this prevents showing the infotext
		mob_def.update_tag = function(self) end
		-- Provide some reward when the monster dies
		mob_def.on_die = function(self)
			set_reward_once(rwd_kill_monster)
		end
	end

	table.insert(spawned_mobs, obj)
end

respawn_objective = function()
	item = minetest.add_item(objective_pos, minetest.settings:get("objective_item"))

	-- Scale the item by some factor
	local scale_factor = 2
	local props = item:get_properties()

	item:set_properties({
		visual_size = {
			x = props.visual_size.x * scale_factor,
			y = props.visual_size.y * scale_factor,
			z = props.visual_size.z * scale_factor,
		},
		collisionbox = {
			props.collisionbox[1] * scale_factor,
			props.collisionbox[2] * scale_factor,
			props.collisionbox[3] * scale_factor,
			props.collisionbox[4] * scale_factor,
			props.collisionbox[5] * scale_factor,
			props.collisionbox[6] * scale_factor,
		},
		selectionbox = {
			props.selectionbox[1] * scale_factor,
			props.selectionbox[2] * scale_factor,
			props.selectionbox[3] * scale_factor,
			props.selectionbox[4] * scale_factor,
			props.selectionbox[5] * scale_factor,
			props.selectionbox[6] * scale_factor,
		},
	})

	-- Override the 'on_punch' callback for this item to provide some reward when collected
	item:get_luaentity().on_punch = function(self, _puncher)
		set_reward_once(rwd_objective, 0.0)
		set_termination()
	end
end

minetest.register_on_joinplayer(function(player, _last_login)
	-- Disable HUD elements
	player:hud_set_flags({
		crosshair = false,
		basic_debug = false,
		healthbar = false,
		hotbar = false,
	})

	-- Generate map and locate the player and monsters
	local map, _ = minetest.settings:get("ascii_map"):gsub("\\n", "\n")
	local material_wall = minetest.settings:get("wall_material")
	local y = 4.5 -- The height of the terrain
	local z = 0
	for row in string.gmatch(map, "[^\n]+") do
		local x = 0
		for c in string.gmatch(row, ".") do
			if c == "#" then
				minetest.set_node({ x = x, y = y, z = z }, { name = material_wall })
			elseif c == "%" then
				minetest.set_node({ x = x, y = y, z = z }, { name = "default:glass" })
			elseif c == "O" then
				objective_pos = { x = x, y = y + 1, z = z }
				respawn_objective()
			elseif c == "-" then
				y = y + 1
				z = -1
				x = -1
			elseif c == "@" then
				player_pos = { x = x, y = y, z = z }
				player:set_pos(player_pos)
			elseif c == "a" then
				local pos = { x = x, y = y, z = z }
				local name = minetest.settings:get("monster_type_a")
				spawn_monster(pos, name)
				table.insert(mobs_info, { pos = pos, name = name })
			elseif c == "b" then
				local pos = { x = x, y = y, z = z }
				local name = minetest.settings:get("monster_type_b")
				spawn_monster(pos, name)
				table.insert(mobs_info, { pos = pos, name = name })
			elseif c == "c" then
				local pos = { x = x, y = y, z = z }
				local name = minetest.settings:get("monster_type_c")
				spawn_monster(pos, name)
				table.insert(mobs_info, { pos = pos, name = name })
			elseif c == "d" then
				local pos = { x = x, y = y, z = z }
				local name = minetest.settings:get("monster_type_d")
				spawn_monster(pos, name)
				table.insert(mobs_info, { pos = pos, name = name })
			end
			x = x + 1
		end
		z = z + 1
	end
end)

minetest.register_on_player_hpchange(function(player, hp_change, reason)
	if player:get_hp() + hp_change <= 0 then -- Check if the player will die
		set_termination()
		return 0 -- Avoid the death of the player that shows the death screen
	end
	return hp_change
end, true)

minetest.register_globalstep(function(dtime)
	-- Set timeofday to midday
	minetest.set_timeofday(0.5)

	-- Reset the environment if requested by the python interface
	if get_soft_reset() == 1 then
		-- Remove the objective item if it's already spawned
		item:remove()
		-- Respawn the objective
		respawn_objective()

		-- Remove all monsters
		for _, mob in ipairs(spawned_mobs) do
			mob:remove()
		end
		spawned_mobs = {}

		-- Respawn all monsters
		for _, info in ipairs(mobs_info) do
			spawn_monster(info.pos, info.name)
		end

		-- Reset player's health and position
		local player = minetest.get_connected_players()[1]
		player:set_hp(20, { type = "set_hp", from = "mod" })
		player:set_pos(player_pos)

		reset_termination()
	end
end)
