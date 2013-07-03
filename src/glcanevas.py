#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '19-06-2013'


from pickle import dump, load

from OpenGL.GL import *
from PyQt4 import QtCore
from PyQt4.QtOpenGL import *

from camera import Camera
from interval import *


class CanevasGLWidget(QGLWidget):

    def __init__(self, parent):
        super(CanevasGLWidget, self).__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(500, 500)

        self.camera = Camera()
        self.camera.setSceneRadius(20)
        self.camera.reset()
        self.oldx = self.oldy = 0
        self.model = Intervals()


    def paintGL(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.camera.transform()
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #glEnable(GL_DEPTH_TEST);    # don't show back faces (test depths)
        #glDepthFunc(GL_LEQUAL);     # test for depth is '<='
        #glEnable(GL_CULL_FACE);     # don't render back faces
        #glFrontFace(GL_CCW);        # back faces are polygons whoses pts are ccw
        #glDisable(GL_LIGHTING);     # disable lighting
        #glShadeModel(GL_FLAT);      # no shades, no light, all same color

        glEnableClientState(GL_VERTEX_ARRAY)
        for array, gl_type, r, g, b in self.model.data:
            glColor(r, g, b)
            glVertexPointer(3, GL_FLOAT, 0, array)
            glDrawArrays(gl_type, 0, len(array))
        glDisableClientState(GL_VERTEX_ARRAY)

        # Draw axis
        glColor(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex(10, 0, 0)
        glEnd()
        glColor(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0,10, 0)
        glEnd()
        glColor(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0, 0,10)
        glEnd()

        glFlush()


    def resizeGL(self, widthInPixels, heightInPixels):
        self.camera.setViewportDimensions(widthInPixels, heightInPixels)
        glViewport(0, 0, widthInPixels, heightInPixels)


    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)


    def mouseMoveEvent(self, mouseEvent):
        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton :
            # user is dragging
            delta_x = mouseEvent.x() - self.oldx
            delta_y = self.oldy - mouseEvent.y()
            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton :
                if int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
                    self.camera.dollyCameraForward(3*(delta_x+delta_y), False )
                else:
                    self.camera.orbit(self.oldx, self.oldy, mouseEvent.x(), mouseEvent.y())
            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
                self.camera.translateSceneRightAndUp(delta_x, delta_y)
            self.update()
        self.oldx = mouseEvent.x()
        self.oldy = mouseEvent.y()


    def save_data(self, f):
         dump(self.model.interval3D, f, 2) # 2 for better pickling of new-style classes

    def load_data(self, f):
        self.model.init_data(load(f))

