-- Positive reward if a tree block is dug
minetest.register_on_dignode(function(pos, node)
  if string.find(node["name"], "tree") then
     -- Give a 1.0 reward once and then reset reward to 0.0 value
     set_reward_once(1.0, 0.0)
     set_info("amount",get_from_info("amount")+1)
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
      set_info("amount",0)
end)

minetest.register_globalstep(function(dtime)

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
	
end)
