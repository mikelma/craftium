-- Set the random seed
if minetest.settings:has("fixed_map_seed") then
   math.randomseed(minetest.settings:get("fixed_map_seed"))
end

max_spiders = 5
num_spiders = 1
dead_spiders = 0
spawn_pos = {x = -2.5, y = 5, z = -10}

spawn_monster = function(pos)
   minetest.after(1, function()
       local monster = mobs:add_mob(pos, {
           name = "craftium:my_spider",
           ignore_count = true, -- ignores mob count per map area
       })

       -- Disable monster's infotext
       monster.update_tag = function()
       end
   end)
end

mobs:register_mob("craftium:my_spider", {
    docile_by_day = false,
    group_attack = true,
    type = "monster",
    passive = false,
    attack_type = "dogfight",
    reach = 2,
    damage = 3,
    hp_min = 25,
    hp_max = 25,
    armor = 200,
    collisionbox = {-0.8, -0.5, -0.8, 0.8, 0, 0.8},
    visual_size = {x = 1, y = 1},
    visual = "mesh",
    mesh = "mobs_spider.b3d",
    textures = {
    	{"mobs_spider_orange.png"},
    },
    makes_footstep_sound = false,
    sounds = {
       random = "mobs_spider",
       attack = "mobs_spider"
    },
    walk_velocity = 1,
    run_velocity = 3,
    jump = true,
    view_range = 20,
    floats = 1,
    drops = {},
    water_damage = 5,
    lava_damage = 5,
    light_damage = 0,
    node_damage = false,
    animation = {
    	speed_normal = 15,
    	speed_run = 20,
    	stand_start = 0,
    	stand_end = 0,
    	walk_start = 1,
    	walk_end = 21,
    	run_start = 1,
    	run_end = 21,
    	punch_start = 25,
    	punch_end = 45
    },

    -- make spiders jump at you on attack
    custom_attack = function(self, pos)
       local vel = self.object:get_velocity()

       self.object:set_velocity({
             x = vel.x * self.run_velocity,
             y = self.jump_height * 1.5,
             z = vel.z * self.run_velocity
       })

       self.pausetimer = 0.5

       return true -- continue rest of attack function
    end,

    on_die = function(self, pos)
       -- Set reward to 1.0 for a single timestep
       set_reward_once(1.0, 0.0)

       -- Increase number of dead spiders
       dead_spiders = dead_spiders + 1

       if dead_spiders < num_spiders then
          return -- One or more spider is still alive!
       end

       -- At this point, all spiders are dead...
       -- prepare the next round!
       dead_spiders = 0
       num_spiders = num_spiders + 1

       -- If the maximum number of spiders is surpassed, finish the episode
       if num_spiders > max_spiders then
          set_termination()
          return
       end

       -- Else, spawn more spiders
       for i=1,num_spiders do
          spawn_monster({ x = 3.7 - i, y = spawn_pos.y, z = spawn_pos.z})
       end
    end
})

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
    -- Set the players initial position and yaw
    player:set_pos({x = -2.5, y = 4.5, z = -1.7})
    player:set_look_horizontal(3.1416) -- Look to the spiders' spawn point

    spawn_monster(spawn_pos)

    -- Disable HUD elements
    player:hud_set_flags({
          hotbar = false,
          crosshair = false,
          healthbar = false,
    })
end)

minetest.register_globalstep(function(dtime)
    -- Set timeofday to midday
    minetest.set_timeofday(0.5)
end)

minetest.register_on_dieplayer(function(_player, _reason)
      -- End episode if the player dies
      set_termination()
end)
