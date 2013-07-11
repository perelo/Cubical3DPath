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

        btn_save = QtGui.QPushButton("Save")
        self.connect(btn_save, QtCore.SIGNAL('clicked()'), self.btn_save_action)

        btn_load = QtGui.QPushButton("Load")
        self.connect(btn_load, QtCore.SIGNAL('clicked()'), self.btn_load_action)

        chk_draw_axis = QtGui.QCheckBox("Draw axis")
        chk_draw_axis.setChecked(self.canevas.draw_axis)
        chk_draw_axis.stateChanged.connect(self.chk_draw_axis_action)

        self.chk_draw_projs = QtGui.QCheckBox("Draw projs")
        self.chk_draw_projs.stateChanged.connect(self.chk_draw_projs_action)

        # Place the buttons
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(btn_reset)
        vbox.addWidget(btn_generate)
        vbox.addWidget(btn_save)
        vbox.addWidget(btn_load)
        vbox.addWidget(chk_draw_axis)
        vbox.addWidget(self.chk_draw_projs)
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
        self.chk_draw_projs_action(self.chk_draw_projs.checkState())
        self.canevas.update()

    def btn_save_action(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save intervals as binary file', 'data.i3db', 'Interval3D (*.i3db*)')
        if file_name:
            f = open(file_name, 'w')
            self.canevas.save_data(f)
            f.close()

    def btn_load_action(self):
        file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open binary intervals file', '', 'Interval3D (*.i3db*)')
        if file_name:
            f = open(file_name, 'r')
            self.canevas.load_data(f)
            f.close()

    def chk_draw_axis_action(self, state):
        self.canevas.draw_axis = (state == QtCore.Qt.Checked)
        self.canevas.update()

    def chk_draw_projs_action(self, state):
        if state == QtCore.Qt.Checked:
            self.canevas.model.add_projections()
        else:
            self.canevas.model.remove_projections()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
