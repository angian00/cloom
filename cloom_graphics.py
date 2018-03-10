
from PyQt5 import QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import *
import moderngl
import numpy as np



REFRESH_RATE = 24 #fps


class GameWidget(QtOpenGL.QGLWidget):
    def __init__(self, game_state):
        self.game_state = game_state

        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)

        #self.timer = QtCore.QElapsedTimer()
        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self.refresh)
        self.refreshTimer.start(1000.0/REFRESH_RATE)

        super(GameWidget, self).__init__(fmt, None)
        self.setWindowTitle("CLOOM")


    def initializeGL(self):
        self.resize(512, 512)
        self.ctx = moderngl.create_context()
        self.ctx.viewport = (0, 0, 512, 512)
        self.screen = self.ctx.detect_framebuffer()

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                //uniform vec2 Pan;
                in vec2 in_vert;
                //in vec4 in_color;
                //out vec4 v_color;
                void main() {
                    //v_color = in_color;
                    //gl_Position = vec4(in_vert - Pan, 0.0, 1.0);
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    //gl_PointSize = 10.0;
                }
            ''',
            fragment_shader='''
                #version 330
                //in vec4 v_color;
                out vec4 f_color;
                void main() {
                    //f_color = v_color;
                    f_color = vec4(0.6, 0.0, 0.0, 0.0);
                }
            ''',
        )

        self.vbo = self.ctx.buffer(reserve='4MB', dynamic=True)
        #self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')



    def paintGL(self):
        data = to_line_data(self.game_state.geometry)

        self.screen.use()
        #self.ctx.clear(0.8, 1.0, 1.0, 1)
        self.ctx.clear(1.0, 1.0, 0.8, 1)
        
        self.vbo.orphan()
        self.vbo.write(data)
        self.ctx.line_width = 4
        self.vao.render(moderngl.LINES)



    def refresh(self):
    	self.updateGL()
    	pass


def to_line_data(geom):
    vv = geom["vv"]
    ll = geom["ll"]

    xx = np.zeros(len(ll)*2)
    yy = np.zeros(len(ll)*2)
    
    for i in range(len(ll)):
        line = ll[i]
        xx[2*i] = vv[line["start"]]["x"]
        yy[2*i] = vv[line["start"]]["y"]
        xx[2*i+1] = vv[line["end"]]["x"]
        yy[2*i+1] = vv[line["end"]]["y"]

    # -768.0 3808.0 -4864.0 -2048.0
    #print(min(xx), max(xx), min(yy), max(yy))

    xx = xx / max(abs(xx))
    yy = yy / max(abs(yy))

    return np.dstack([xx, yy]).astype("f4").tobytes()
