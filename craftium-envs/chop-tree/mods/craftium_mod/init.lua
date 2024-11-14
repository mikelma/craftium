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
