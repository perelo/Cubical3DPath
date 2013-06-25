#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


import numpy as np
from OpenGL.GL import *     # types : GL_POINTS, GL_LINES, ...
from geom import *
import util


class Interval:

    def __init__(self):
        self.data = []      # list of tuples (list of data, type, r, g, b)
        self.init_data()


    def init_data(self):
        #self.l_reconstructed()

        intervals = Interval.gen_3_intervals(5, 5, 25, 25, 2)
        flat_intervals = [util.flat_points(interval) for interval in intervals]
        self.data = [(interval, GL_LINE_LOOP, 1, 0, 0)
                            for interval in flat_intervals]


    @staticmethod
    def gen_3_intervals(xMin, yMin, xMax, yMax, step_size = 1):
        intervalxy = Interval.generate_interval2D(xMin, yMin, xMax, yMax, step_size)
        intervalxz = Interval.generate_interval2D(xMin, yMin, xMax, yMax, step_size)
        intervalyz = Interval.generate_interval2D(xMin, yMin, xMax, yMax, step_size)

        intervalxy = [Point3D(p2D.x(), p2D.y(), 0) for p2D in intervalxy]
        intervalxz = [Point3D(p2D.y(), 0, p2D.x()) for p2D in intervalxz]
        intervalyz = [Point3D(0, p2D.y(), p2D.x()) for p2D in intervalyz]

        return [intervalxy, intervalxz, intervalyz]


    @staticmethod
    def generate_interval2D(xMin, yMin, xMax, yMax, step_size = 1):
        from random import randrange

        lower_line = [Point2D(xMin, yMin)]
        upper_line = [Point2D(xMin, randrange(yMin, yMax+1, step_size))]

        old_low  = lower_line[0].y()
        old_high = upper_line[0].y()

        lower_line_done = upper_line_done = False
        for i in range(xMin+step_size, xMax, step_size):
            if not lower_line_done:
                low = randrange(old_low, yMax+1, step_size)
                if low >= yMax:
                    lower_line_done = True
                else:
                    if old_low < low:
                        lower_line.append(Point2D(i, old_low))
                        lower_line.append(Point2D(i, low))
                    old_low = low

            if not upper_line_done:
                high = randrange(max(low, old_high), yMax+1, step_size)
                if old_high < high:
                    upper_line.append(Point2D(i, old_high))
                    upper_line.append(Point2D(i, high))
                if high >= yMax:
                    upper_line_done = True
                old_high = high
        upper_line.append(Point2D(xMax, yMax))
        lower_line.append(Point2D(xMax, old_low))

        upper_line.reverse()
        lower_line.extend(upper_line)
        return lower_line


    @staticmethod
    def write_2d_intervals(f, xy, xz, yz):
        f.write('xy\n')
        for p in xy:
            f.write('{0[0]} {0[1]} {0[2]}\n'.format(p.get()))
        f.write('\nxz\n')
        for p in xz:
            f.write('{0[0]} {0[1]} {0[2]}\n'.format(p.get()))
        f.write('\nyz\n')
        for p in yz:
            f.write('{0[0]} {0[1]} {0[2]}\n'.format(p.get()))
        f.write('\n')

