(Yet Another) Superflat Map Generator [superflat]
=========

# License
MIT License (code) and CC BY-SA 3.0 (media) (see LICENSE file)

# Features
- Customize world generation layer by layer
- Decoration (optional)
- If you fall, you will be returned to the surface

# How to Modify
1. Open parameter.lua file.
2. Change sflat.Y_ORIGIN to adjust first layer's y-level (default: 1).
3. Change sflat.BLOCKS to adjust the composition of the world (code: layers from bottom to top;biome,decoration) (examples below).

Note: If the specified node does not exist, the air node will be used.

## Modify an Existing World
1. Open superflat.txt file in your world's folder.
2. Do like editing parameter.lua file.

## List of Biomes
Note: Biome decorations are only available with the "default" mod (Minetest Game or its derivatives).
- Frozen River (no decoration for now)
- River (no decoration for now)
- Ice Plains (no decoration for now)
- Ice Plains Spikes
- Flower Plains
- Plains
- Forest
- Jungle
- Desert

## Examples
Name
	Code

Example
	"node:name_bottom=amount,node:name_top=amount"
Example (+decoration)
	"node:name_bottom=amount,node:name_top=amount;Biome,decoration"
Example (one layer thick)
	"node:a,node:b=2,node:c=3"

Default
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass"
Forest
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass;Forest,decoration"
Flower Garden
	"superflat:bedrock,default:dirt=2,default:dirt_with_grass;Flower Plains,decoration"
Shallow Underground
	"superflat:bedrock,default:stone=230,default:dirt=5,default:dirt_with_grass"
Deep Underground
	"superflat:bedrock,default:stone=920,default:dirt=10,default:dirt_with_grass"
Very Deep Underground
	"superflat:bedrock,default:stone=3680,default:dirt=15,default:dirt_with_grass"
Bottomless Pit
	"default:cobble=2,default:dirt=3,default:dirt_with_grass"
Shallow Sea
	"superflat:bedrock,default:dirt=3,default:water_source=5"
Sea
	"superflat:bedrock,default:dirt=3,default:water_source=10"
Deep Sea
	"superflat:bedrock,default:dirt=3,default:water_source=20"
Water World
	"superflat:bedrock,default:dirt=3,default:water_source=60"
Beach
	"superflat:bedrock,default:sand=3,default:water_source"
Desert Superflat
	"superflat:bedrock,default:desert_sand=3"
Farmer's Dream
	"superflat:bedrock,default:water_source,farming:soil_wet"
You Cannot Escape
	"default:gravel,default:sand,default:gravel"
