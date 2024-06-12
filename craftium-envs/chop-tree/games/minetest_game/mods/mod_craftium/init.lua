-- Positive reward if a dirt block is dug
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
