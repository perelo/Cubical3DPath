#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


from OpenGL.GL import *     # types : GL_POINTS, GL_LINES, ...

import generation as gen
from geom import *
import util


class Intervals:

    def __init__(self):
        self.data = []      # list of tuples (list of data, type, r, g, b)
        self.init_data()


    def init_data(self, interval3D=None):
        p_min = Point3D(5, 5, 5)
        p_max = Point3D(15, 15, 15)
        step = 2

        self.interval3D = gen.generate_interval3D(p_min, p_max, step) \
                                if not interval3D else interval3D

        self.data = [(util.flat_segments(self.interval3D.segments), GL_LINES, 1, 1, 1)]

        self.proj_tuples = []
        for proj in self.interval3D.get_projected_segments():
            self.proj_tuples.append((util.flat_segments(proj), GL_LINES, 1, 0, 0))


    def add_projections(self):
        if self.proj_tuples not in self.data:
            self.data.extend(self.proj_tuples)

    def remove_projections(self):
        if self.proj_tuples[0] in self.data:
            for t in self.proj_tuples:
                self.data.remove(t)


    @staticmethod
    def write_2d_intervals(f, xy, xz, yz):
        f.write('xy\n')
        f.write(str(xy))
        f.write('\nxz\n')
        f.write(str(xz))
        f.write('\nyz\n')
        f.write(str(yz))
        f.write('\n')


class Interval2D:

    def __init__(self, points=[]):
        self.points = points

    def __str__(self):
        return '\n'.join(' '.join(str(coord) for coord in p.get()) for p in self.points)


class Interval3D:

    def __init__(self, segments=[]):
        self.segments = segments

    def get_projected_segments(self):
        xy = [Segment3D(Point3D(e.a.x(), e.a.y(), 0), Point3D(e.b.x(), e.b.y(), 0))
                                                        for e in self.segments if e.a.z() == e.b.z()]
        xz = [Segment3D(Point3D(e.a.x(), 0, e.a.z()), Point3D(e.b.x(), 0, e.b.z()))
                                                        for e in self.segments if e.a.y() == e.b.y()]
        yz = [Segment3D(Point3D(0, e.a.y(), e.a.z()), Point3D(0, e.b.y(), e.b.z()))
                                                        for e in self.segments if e.a.x() == e.b.x()]
        return (xy, xz, yz)

