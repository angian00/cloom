
import os.path
import numpy as np
from enum import Enum



HEADER_SIZE = 12
DIR_ENTRY_SIZE = 16

LINEDEF_SIZE = 14
VERTEXES_SIZE = 4


class ParseState(Enum):
	normal = 0
	inside_level = 1
	inside_sprites = 2
	inside_patches = 3
	inside_flats = 4


class Wad():
	def __init__(self, filename):
		f = open(filename, "rb")
		raw_data = f.read()
		f.close()

		self.ident = to_str(raw_data[0:4])
		self.num_lumps = to_int(raw_data[4:8])
		self.dir_offset = to_int(raw_data[8:12])

		self.metadata = {
			"ident": self.ident,
			"num_lumps": self.num_lumps,
			"dir_offset": self.dir_offset,
		}

		self.read_dir(raw_data)
		self.read_lumps(raw_data)



	def read_dir(self, raw_data):
		global parse_state

		self.lumps = []
		dir_data = raw_data[self.dir_offset:]

		parse_state = ParseState.normal
		for i in range(self.num_lumps):
			dir_entry = {}
			dir_entry_data = dir_data[DIR_ENTRY_SIZE * i : DIR_ENTRY_SIZE * (i+1)]
			dir_entry["file_pos"] = to_int(dir_entry_data[0:4])
			dir_entry["size"] = to_int(dir_entry_data[4:8])
			dir_entry["name"] = to_str(dir_entry_data[8:16])
			#print(dir_entry["name"])
			self.lumps.append(dir_entry)


	def read_lumps(self, raw_data):
		global parse_state

		levels = {}
		images = {}

		for lump in self.lumps:
			lump_data = raw_data[lump["file_pos"] : lump["file_pos"] + lump["size"]]
			#DEBUG
			# print(lump["name"])
			# if lump["name"] == "FLOOR0_1":
			# 	print(lump)
			# 	print(lump_data)

			if parse_state == ParseState.normal:
				if lump["name"] == "S_START":
					parse_state = ParseState.inside_sprites

				elif lump["name"] == "P1_START" or lump["name"] == "P2_START":
					parse_state = ParseState.inside_patches

				elif lump["name"] == "F1_START" or lump["name"] == "F2_START":
					parse_state = ParseState.inside_flats

				elif lump["name"] == "E1M1":
					level_name = lump["name"]
					parse_state = ParseState.inside_level

				elif lump["name"] == "PLAYPAL":
					self.palettes = read_palettes(lump_data)

				elif lump["name"] == "PNAMES":
					self.pnames = read_pnames(lump_data)

				elif lump["name"] == "TEXTURE1":
					self.textures = read_textures(lump_data)

				# elif lump["name"] == "WISCRT2": # "SECRET" label image
				# 	images[lump["name"]] = read_image(lump_data)

				# elif lump["name"] == "WIENTER": # "ENTERING" label image
				# 	images[lump["name"]] = read_image(lump_data)

				else:
					pass


			elif parse_state == ParseState.inside_sprites:
				if lump["name"] == "S_END":
					parse_state = ParseState.normal
				else:
					images[lump["name"]] = read_image(lump_data)

			elif parse_state == ParseState.inside_patches:
				if lump["name"] == "P1_END" or lump["name"] == "P2_END":
					parse_state = ParseState.normal
				else:
					#images[lump["name"]] = read_image(lump_data, debug=(lump["name"] == "WALL00_3"))
					images[lump["name"]] = read_image(lump_data)

			elif parse_state == ParseState.inside_flats:
				if lump["name"] == "F1_END" or lump["name"] == "F2_END":
					parse_state = ParseState.normal
				else:
					#TODO: parse flats
					#images[lump["name"]] = read_image(lump_data)
					pass


			elif parse_state == ParseState.inside_level:
				if lump["name"] == "LINEDEFS":
					linedefs = read_linedefs(lump_data)

				elif lump["name"] == "VERTEXES":
					vertexes = read_vertexes(lump_data)

				elif lump["name"] == "BLOCKMAP":
					#graphics.show_level(vertexes, linedefs)
					levels[level_name] = {"vv": vertexes, "ll": linedefs}
					parse_state = ParseState.normal
					
				else:
					# THINGS
					# LINEDEFS
					# SIDEDEFS
					# VERTEXES
					# SEGS
					# SSECTORS
					# NODES
					# SECTORS
					# REJECT
					# BLOCKMAP
					pass

			self.levels = levels
			self.images = images


	def build_texture_image(self, t):
		t_img = np.zeros((t["width"], t["height"]))
		print("build_texture_image [{}]".format(t))
		for p in t["patches"]:
			x_off = p["x_offset"]
			y_off = p["y_offset"]
			p_name = self.pnames[p["i_pnames"]]
			p_img = self.images[p_name]
			w, h = p_img.shape
			#print("{}: {}x{}".format(p_name, w,h))
			#ignore errors on array sizes 
			try:
				t_img[x_off:x_off+w, y_off:y_off+h] = p_img[0:w, 0:h]
			except ValueError:
				pass

		return t_img


def read_palettes(lump_data):
	palettes = []
	# 256 R,G,B bytes per palette
	for i in range(int(len(lump_data) / (256*3))):
		palette = lump_data[i*(256*3) : (i+1)*(256*3)]
		palettes.append(palette)

	return palettes


def read_pnames(lump_data):
	pnames = []

	n_pnames = to_int(lump_data[0:4])
	for i in range(n_pnames):
		pnames.append(to_str(lump_data[4+8*i:4+8*(i+1)]))

	return pnames


def read_textures(lump_data):
	textures = {}

	n_textures = to_int(lump_data[0:4])
	for i_t in range(n_textures):
		t_offset = to_int(lump_data[(i_t+1)*4:(i_t+2)*4])

		t_name  = to_str(lump_data[t_offset:t_offset+8])
		t_width   = to_int(lump_data[t_offset+12:t_offset+14])
		t_height  = to_int(lump_data[t_offset+14:t_offset+16])
		n_patches = to_int(lump_data[t_offset+20:t_offset+22])

		#DEBUG
		#if n_patches != 1:
		#	continue
		#print("[{}] {}: {}x{} - {}".format(i_t, t_name, t_width, t_height, n_patches)) #DEBUG

		t_patches = []
		for i_patch in range(n_patches):
			p_offset = (t_offset + 22) + 5*i_patch

			x_off    = to_int(lump_data[p_offset:p_offset+2])
			y_off    = to_int(lump_data[p_offset+2:p_offset+4])
			i_pnames = to_int(lump_data[p_offset+4:p_offset+6])
			
			t_patches.append({"x_offset": x_off, "y_offset": y_off, "i_pnames": i_pnames})

		textures[t_name] = {"name": t_name, "width": t_width, "height": t_height, "patches": t_patches}

	return textures


def read_image(lump_data, debug=False):
	w = to_int(lump_data[0:2])
	h = to_int(lump_data[2:4])
	left_offset = to_int(lump_data[4:6])
	top_offset  = to_int(lump_data[6:8])

	if debug:
		print("read_image: {}x{}, +{} +{}".format(w, h, left_offset, top_offset))
		print(lump_data)
	#print(w,h)
	pixel_data = np.zeros((h, w))

	col_offsets = []
	for i in range(w):
		col_offset = to_int(lump_data[8 + 4*i : 8 + 4*(i+1)])
		col_offsets.append(col_offset)


	for i in range(w):
		curr_offset = col_offsets[i]
		b = lump_data[curr_offset]
		
		while b != 0xff:
			start_row = b
			n_rows = lump_data[curr_offset+1]

			for j in range(n_rows):
				pixel_data[start_row+j][i] = lump_data[curr_offset + j + 1 + 2]

			curr_offset = curr_offset + n_rows + 4
			b = lump_data[curr_offset]


	# im = Image.fromarray((pixel_data).astype('uint8'), 'P')
	# im.putpalette(self.palettes[0])

	# im.show()

	return pixel_data



def read_linedefs(lump_data):
	linedefs = []
	for i in range(int(len(lump_data) / LINEDEF_SIZE)):
		ld = lump_data[i*LINEDEF_SIZE : (i+1)*LINEDEF_SIZE]
		start_v = to_int(ld[0:2])
		end_v = to_int(ld[2:4])
		linedefs.append({"start": start_v, "end": end_v})

	return linedefs


def read_vertexes(lump_data):
	vertexes = []
	for i in range(int(len(lump_data) / VERTEXES_SIZE)):
		vv = lump_data[i*VERTEXES_SIZE : (i+1)*VERTEXES_SIZE]
		x = to_int(vv[0:2])
		y = to_int(vv[2:4])
		vertexes.append({"x": x, "y": y})

	return vertexes


def to_int(bytes):
	return int.from_bytes(bytes, byteorder='little', signed=True)

def to_str(bytes):
	return bytes.decode("ascii").rstrip("\0")

