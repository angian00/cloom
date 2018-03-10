#!/usr/bin/env python3


from cloom_graphics import GameWidget
from cloom_parser import Wad
from cloom_game import GameState

import os.path
from PyQt5 import QtWidgets


WAD_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/doom1.wad"



def main():
    game_data = Wad(WAD_PATH)

    game_state = GameState(game_data)

    app = QtWidgets.QApplication([""])

    gui = GameWidget(game_state)
    gui.show()


    while game_state.is_running: 
        app.processEvents()

        #TODO: game state update


    sys.exit(app.exec_())



if __name__ == '__main__':
    main()

