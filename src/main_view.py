#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '19-06-2013'


import math
import sys

from PyQt4 import QtGui, QtCore

from glcanevas import CanevasGLWidget


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.move(100, 100)
        self.setWindowTitle('Shortest path in cubical complex')

        # Create main canevas that will render the OpenGL scene
        self.canevas = CanevasGLWidget(self)

        # Create buttons
        btn_reset = QtGui.QPushButton("Reset")
        btn_reset.setStatusTip('Reset camera')
        self.connect(btn_reset, QtCore.SIGNAL('clicked()'), self.btn_reset_action)
        btn_generate = QtGui.QPushButton("Generate")
        btn_generate.setToolTip('Generate random 2D intervals on the 3 planes')
        self.connect(btn_generate, QtCore.SIGNAL('clicked()'), self.btn_generate_action)

        # Place the buttons
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(btn_reset)
        vbox.addWidget(btn_generate)
        vbox.addStretch(1)

        # Place main components
        self.canevas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.canevas)

        parent_widget = QtGui.QWidget()
        parent_widget.setLayout(hbox)
        self.setCentralWidget(parent_widget)

        #self.resize(500,500)


    def btn_reset_action(self):
        self.canevas.camera.reset()
        self.canevas.update()


    def btn_generate_action(self):
        self.canevas.model.init_data()
        self.canevas.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
