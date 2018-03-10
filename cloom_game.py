

class GameState():
	def __init__(self, game_data):
		self.geometry = game_data.levels["E1M1"]
		self.is_running = True
