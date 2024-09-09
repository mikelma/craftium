
-- Names of the items included in the initial inventory
init_tools = { "mcl_tools:axe_stone", "mcl_torches:torch 256" }

timeofday_step = 1 / 5000 -- day/night cycle lasts 5000 steps
timeofday = 0.5 -- start episode at midday

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
      minetest.set_timeofday(timeofday)

      -- Disable HUD elements
      player:hud_set_flags({
            crosshair = false,
            basic_debug = false,
            chat = false,
      })

      -- Setup initial inventory
      local inv = player:get_inventory()
      for i=1, #init_tools do
         inv:add_item("main", init_tools[i])
      end
end)

-- Turn on the termination flag if the agent dies
minetest.register_on_dieplayer(function(ObjectRef, reason)
      set_termination()
end)

-- Make game's time to match with learning timesteps
minetest.register_globalstep(function(dtime)
      if timeofday > 1.0 then
         timeofday = 0.0
      end
      minetest.set_timeofday(timeofday)
      timeofday = timeofday + timeofday_step
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
   { name = "end" }
}

curr_stage = 1 -- index of the current stage

minetest.register_on_dignode(function(pos, node)
      -- table of the next stage
      local snext = stages[curr_stage+1]

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
         print(string.format("[STAGE] Stage '%s' starts", snext.name))

         -- provide one timestep reward
         set_reward_once(snext.reward, 0.0)

         -- add new tools to the inventory (removing the current ones first)
         for _, player in pairs(minetest.get_connected_players()) do
            local inv = player:get_inventory()
            inv:set_list("main", {}) -- empty inventory
            for i=1, #init_tools do -- reset initial inventory (in the same slots)
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

mob_setup = {
   -- Defending
   ["mobs_mc:zombie"] = { die_reward = 32.0 },
   ["mobs_mc:skeleton"] = { die_reward = 64.0 },
   ["mobs_mc:spider"] = { die_reward = 128.0 },
   ["mobs_mc:cave_spider"] = { die_reward = 256.0 },
   -- Hunting
   ["mobs_mc:chicken"] = { die_reward = 16.0 },
   ["mobs_mc:sheep"] = { die_reward = 32.0 },
   ["mobs_mc:pig"] = { die_reward = 64.0 },
   ["mobs_mc:cow"] = { die_reward = 128.0 },
}

for name, _ in pairs(mcl_mobs.spawning_mobs) do -- for all mobs that spawn
   local setup = mob_setup[name]
   -- access its definition
   local mod_def = minetest.registered_entities[name]
   -- if the mob is considered for the environment
   if setup ~= nil then
      -- change on_die callback to provide reward
      local old_fn = mod_def.on_die
      mod_def.on_die = function(self)
         print(">> [HUNT/DEFEND] Mob died:", name)
         set_reward_once(setup.die_reward, 0.0)
         if old_fn ~= nil then
            old_fn(self)
         end
      end
   else
      mod_def.chance = 10000 -- Set an absurdly low spawining prob.
   end
end
