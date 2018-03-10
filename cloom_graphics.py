
from PyQt5 import QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import *
import moderngl


REFRESH_RATE = 24 #fps


class GameWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)

        #self.timer = QtCore.QElapsedTimer()
        super(GameWidget, self).__init__(fmt, None)
        self.setWindowTitle("CLOOM")

        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self.refresh)
        self.refreshTimer.start(1000.0/REFRESH_RATE)



    def initializeGL(self):
        self.resize(512, 512)
        self.ctx = moderngl.create_context()
        self.ctx.viewport = (0, 0, 512, 512)
        self.screen = self.ctx.detect_framebuffer()
        pass

    def paintGL(self):
        # self.resize(512, 512)
        # self.ctx = moderngl.create_context()
        # self.ctx.viewport = (0, 0, 512, 512)
        # self.screen = self.ctx.detect_framebuffer()

        self.screen.use()
        self.ctx.clear(0.6, 0.8, 1.0, 0)


    def refresh(self):
    	#self.updateGL()
    	pass


