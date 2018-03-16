#!/usr/bin/env python3

import os.path
from PIL import Image
from cloom_parser import Wad


WAD_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/doom1.wad"

def main():
	game_data = Wad(WAD_PATH)
	
	# print("--Textures:")
	# for tn in game_data.textures:
	# 	t = game_data.textures[tn]
	# 	if len(t["patches"]) > 1:
	# 		print(t)
	
	# for i in range(len(game_data.pnames)):
	# 	pn = game_data.pnames[i]
	# 	print("[{}] {}".format(i, pn))

	img_data = game_data.build_texture_image(game_data.textures["SW2STON1"])
	im = Image.fromarray((img_data).astype('uint8'), 'P')
	im.putpalette(game_data.palettes[0])
	im.show()


if __name__ == '__main__':
    main()


