#!/usr/bin/env python3

from cloom_graphics import GameWidget
from cloom_parser import Wad


from PyQt5 import QtWidgets


WAD_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/doom1.wad"



def main():
    app = QtWidgets.QApplication([""])

    gui = GameWidget()
    gui.show()

    game_data = Wad(WAD_PATH)


    game_running = True
    while game_running: 
        app.processEvents()

        #TODO: game state update


    sys.exit(app.exec_())



if __name__ == '__main__':
    main()

