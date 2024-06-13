--------------------------------
--         Parameter          --
-- Modify the parameters here --
--------------------------------

-- These parameters only apply to new world.
-- For an existing world, edit superflat.txt file in its folder.

-- Start of the superflat layers
sflat.Y_ORIGIN = 1
-- Composition (layer by layer)
sflat.BLOCKS = "superflat:bedrock,default:dirt=2,default:dirt_with_grass"

--[[

-- EXAMPLE
	"node:name_bottom=amount,node:name_top=amount"
	"node:name_bottom=amount,node:name_top=amount;Biome,decoration" (with decoration)
	"node:a,node:b=2,node:c=3" (no amount means one block thick)
	Note: Biome decorations are only available with the `default` mod (Minetest Game or its derivatives).

-- SUPERFLAT: Default
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass"

-- SUPERFLAT: Forest
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass;Forest,decoration"

-- SUPERFLAT: Flower Garden
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass;Flower Plains,decoration"

-- SUPERFLAT: Shallow Underground
	"superflat:bedrock,default:stone=230,default:dirt=5,default:dirt_with_grass"

-- SUPERFLAT: Deep Underground
	"superflat:bedrock,default:stone=920,default:dirt=10,default:dirt_with_grass"

-- SUPERFLAT: Very Deep Underground
	"superflat:bedrock,default:stone=3680,default:dirt=15,default:dirt_with_grass"

-- SUPERFLAT: Bottomless Pit
	"default:cobble=2,default:dirt=3,default:dirt_with_grass"

-- SUPERFLAT: Shallow Sea
	"superflat:bedrock,default:dirt=3,default:water_source=5"

-- SUPERFLAT: Sea
	"superflat:bedrock,default:dirt=3,default:water_source=10"

-- SUPERFLAT: Deep Sea
	"superflat:bedrock,default:dirt=3,default:water_source=20"

-- SUPERFLAT: Water World
	"superflat:bedrock,default:dirt=3,default:water_source=60"

-- SUPERFLAT: Beach
	"superflat:bedrock,default:sand=3,default:water_source"

-- SUPERFLAT: Desert
	"superflat:bedrock,default:desert_sand=3"

-- SUPERFLAT: Farmer's Dream
	"superflat:bedrock,default:water_source,farming:soil_wet"
	
-- SUPERFLAT: You Cannot Escape
	"default:gravel,default:sand,default:gravel"

--]]
