
import os.path
import numpy as np
from PIL import Image



HEADER_SIZE = 12
DIR_ENTRY_SIZE = 16

LINEDEF_SIZE = 14
VERTEXES_SIZE = 4




class Wad():
	def __init__(self, filename):
		f = open(filename, "rb")
		raw_data = f.read()
		f.close()

		self.ident = raw_data[0:4]
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
		self.lumps = []
		dir_data = raw_data[self.dir_offset:]

		for i in range(self.num_lumps):
			dir_entry = {}
			dir_entry_data = dir_data[DIR_ENTRY_SIZE * i : DIR_ENTRY_SIZE * (i+1)]
			dir_entry["file_pos"] = to_int(dir_entry_data[0:4])
			dir_entry["size"] = to_int(dir_entry_data[4:8])
			dir_entry["name"] = to_str(dir_entry_data[8:16])
			#print(dir_entry["name"])
			self.lumps.append(dir_entry)


	def read_lumps(self, raw_data):
		inside_level = False
		levels = {}
		images = {}

		for lump in self.lumps:
			lump_data = raw_data[lump["file_pos"] : lump["file_pos"] + lump["size"]]

			if inside_level:
				if lump["name"] == "LINEDEFS":
					linedefs = read_linedefs(lump_data)

				elif lump["name"] == "VERTEXES":
					vertexes = read_vertexes(lump_data)

				elif lump["name"] == "BLOCKMAP":
					inside_level = False
					#graphics.show_level(vertexes, linedefs)
					levels[level_name] = {"vv": vertexes, "ll": linedefs}

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

			else:
				if lump["name"] == "E1M1":
					level_name = lump["name"]
					inside_level = True

				if lump["name"] == "PLAYPAL":
					self.palettes = read_palettes(lump_data)

				elif lump["name"] == "WISCRT2": # "SECRET" label image
					images[lump["name"]] = read_image(lump_data)

				elif lump["name"] == "WIENTER": # "ENTERING" label image
					images[lump["name"]] = read_image(lump_data)

			self.levels = levels
			self.images = images



def read_palettes(lump_data):
	palettes = []
	# 256 R,G,B bytes per palette
	for i in range(int(len(lump_data) / (256*3))):
		palette = lump_data[i*(256*3) : (i+1)*(256*3)]
		palettes.append(palette)

	return palettes


def read_image(lump_data):
	w = to_int(lump_data[0:2])
	h = to_int(lump_data[2:4])
	left_offset = to_int(lump_data[4:6])
	top_offset  = to_int(lump_data[6:8])

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

