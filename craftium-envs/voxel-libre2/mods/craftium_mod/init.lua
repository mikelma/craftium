-- names of the items included in the initial inventory
init_tools = { "mcl_tools:axe_stone", "mcl_torches:torch 256" }

timeofday_step = 1 / (10000 * minetest.settings:get("frameskip")) -- day/night cycle lasts 10K steps
timeofday = 0.5 -- start episode at midday

-- executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
	minetest.set_timeofday(timeofday)

	-- disable HUD elements
	player:hud_set_flags({
		crosshair = false,
		basic_debug = false,
		chat = false,
	})

	-- setup initial inventory
	local inv = player:get_inventory()
	for i = 1, #init_tools do
		inv:add_item("main", init_tools[i])
	end

	-- set player's initial position
	player:set_pos({ x = 120, z = 92, y = 16.5 })

	-- initialize values and dictionaries
	set_info("damage_taken",0.0)
	set_info("damage_dealt",0.0)
	set_info("healed_amount",0.0)

	set_empty_dict("mined_nodes")
	set_empty_dict("defeated_enemies")
	set_empty_dict("hunted_animals")
end)

-- turn on the termination flag if the agent dies
minetest.register_on_dieplayer(function(ObjectRef, reason)
	-- get cause of death
    if reason then
        if reason.type == "punch" then
            if reason.object then
                if reason.object:is_player() then
                    cause_msg = "Was slain by another player"
                else
                    local entity = reason.object:get_luaentity()
                    if entity and entity.name then
                        cause_msg = "was killed by a mob or entity: " .. entity.name .. "."
                    else
                        cause_msg = "was killed by an unknown entity."
                    end
                end
            else
                cause_msg = "was punched to death."
            end

        elseif reason.type == "fall" then
            cause_msg = "fell from a high place."

        elseif reason.type == "drown" then
            cause_msg = "drowned."

        elseif reason.type == "node_damage" then
            if reason.node then
                local nodedef = minetest.registered_nodes[reason.node.name]
                local nodename = nodedef and nodedef.description or reason.node.name
                cause_msg = "died due to contact with " .. nodename .. "."
            else
                cause_msg = "was hurt by a damaging node."
            end

        elseif reason.type == "set_hp" then
            cause_msg = "died due to a script or mod setting their HP to 0."

        else
            cause_msg = "died from an unknown cause (" .. reason.type .. ")."
        end
    end
	set_info("cause_of_death", cause_msg)
	set_termination()
end)

-- make game's time match with learning timesteps
minetest.register_globalstep(function(dtime)
	if timeofday > 1.0 then
		timeofday = 0.0
	end
	minetest.set_timeofday(timeofday)
	timeofday = timeofday + timeofday_step

	local player = core.get_connected_players()[1]

	-- if the player is not connected end here
	if player == nil then
		return nil
	end

	-- if the player is connected:
	-- get the position of the player
	local player_pos = player:get_pos()
	set_info("y",player_pos.y)
	set_info("z",player_pos.z)
	set_info("x",player_pos.x)
	
	-- get the health of the player
	set_info("health",player:get_hp())
	
	-- get stage and stage progress
	set_info("stage",curr_stage)
	set_info("progress",stages[curr_stage + 1].current)
	
	-- get inventory
	set_empty_dict("inventory")
	local inv = player:get_inventory()
	local list = inv:get_list("main")
	for i, itemstack in ipairs(list) do
		if not itemstack:is_empty() then
			add_to_dict("inventory",itemstack:get_name(),itemstack:get_count())
		end
	end
end)

--
-- Tools
-- ~~~~~

stages = {
	-- Inital stage
	{ name = "init" },
	-- Wood stage
	{
		name = "wood", -- name of the stage
		req_name = "tree", -- substring included in the target node's name
		req_num = 2, -- number of resources (req_name) required to jump to the next stage
		current = 0, -- number of (target) resources currently obtained
		provides = { "mcl_tools:pick_wood", "mcl_tools:sword_wood" }, -- the tools provided upon completion
		reward = 128.0, -- the reward of completing the stage
	},
	-- Stone stage
	{
		name = "stone",
		req_name = "stone",
		req_num = 3,
		current = 0,
		provides = { "mcl_tools:pick_stone", "mcl_tools:sword_stone" },
		reward = 256.0,
	},
	-- Stone stage
	{
		name = "iron",
		req_name = "iron",
		req_num = 3,
		current = 0,
		provides = { "mcl_tools:pick_iron", "mcl_tools:sword_iron", "mcl_tools:axe_iron" },
		reward = 1024.0,
	},
	{
		name = "diamond",
		req_name = "diamond",
		req_num = 1,
		current = 0,
		provides = { "mcl_tools:pick_diamond", "mcl_tools:sword_diamond", "mcl_tools:axe_diamond" },
		reward = 2048.0,
	},
	{ name = "end" },
}

curr_stage = 1 -- index of the current stage

minetest.register_on_dignode(function(pos, node)
	-- update table of mined nodes of info
	if dict_contains("mined_nodes", node["name"]) then
		add_to_dict("mined_nodes",node["name"],get_from_dict("mined_nodes",node["name"])+1)
	else
		add_to_dict("mined_nodes",node["name"],1)
	end

	-- table of the next stage
	local snext = stages[curr_stage + 1]

	-- there's nothing to do if we reached the last stage
	if snext.name == "end" then
		return
	end

	-- check if the dug node contains the `req_name` substring
	if string.find(node["name"], snext.req_name) then
		snext.current = snext.current + 1
	end

	-- check if we've enough resources to jump to the next stage
	if snext.current >= snext.req_num then
		print(string.format("[STAGE] Stage '%s' starts", snext.name), os.date())

		-- provide one timestep reward
		set_reward_once(snext.reward, 0.0)

		-- add new tools to the inventory (removing the current ones first)
		for _, player in pairs(minetest.get_connected_players()) do
			local inv = player:get_inventory()
			inv:set_list("main", {}) -- empty inventory
			for i = 1, #init_tools do -- reset initial inventory (in the same slots)
				inv:add_item("main", init_tools[i])
			end
			for i = 1, #snext.provides do -- add the unlocked tools
				inv:add_item("main", snext.provides[i])
			end
		end

		-- Move to the next stage
		curr_stage = curr_stage + 1
	end
end)

--
-- Hunt and Defend
-- ~~~~~~~~~~~~~~~

for name, _ in pairs(mcl_mobs.spawning_mobs) do -- for all mobs that spawn
	-- access its definition
	local mob_def = minetest.registered_entities[name]
	local mob_type = mob_def.type
	local old_on_punch = mob_def.on_punch
	mob_def.on_punch = function(self, puncher, time_from_last_punch, tool_capabilities, dir)
		local damage = tool_capabilities.damage_groups and tool_capabilities.damage_groups.fleshy or 1
		if puncher then
			self.last_puncher_is_player = puncher:is_player()
		end
		-- update damage dealt in info
		set_info("damage_dealt",get_from_info("damage_dealt")+damage)
		-- provide a different reward for each type of punched mob
		if mob_type == "monster" then
			set_reward_once(damage, 0.0)
		elseif mob_type == "animal" then
			set_reward_once(damage * 0.5, 0.0)
		elseif mob_type == "npc" then
			set_reward_once(-10.0, 0.0)
		end
		-- Call the original on_punch function
		if old_on_punch ~= nil then
			old_on_punch(self, puncher, time_from_last_punch, tool_capabilities, dir)
		end
	end

	-- update the table of defeated enemies of info
	local old_on_die = mob_def.on_die
	mob_def.on_die = function(self, killer)
		if self.last_puncher_is_player then
			if mob_type == "monster" then
				if dict_contains("defeated_enemies", name) then
					add_to_dict("defeated_enemies",name,get_from_dict("defeated_enemies",name)+1)
				else
					add_to_dict("defeated_enemies",name,1)
				end
			elseif mob_type == "animal" then
				if dict_contains("hunted_animals", name) then
					add_to_dict("hunted_animals",name,get_from_dict("hunted_animals",name)+1)
				else
					add_to_dict("hunted_animals",name,1)
				end
			end
		end

		-- Call the original on_die function
		if old_on_die ~= nil then
			old_on_die(self, killer)
		end
	end
end

minetest.register_on_player_hpchange(function(player, hp_change, reason)
    if hp_change < 0 then
        set_info("damage_taken",get_from_info("damage_taken")-hp_change)
    end
	if hp_change > 0 then
        set_info("healed_amount",get_from_info("healed_amount")+hp_change)
    end
    return hp_change
end, true)
