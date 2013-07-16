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


class Intervals(object):

    def __init__(self):
        self.data = []      # list of tuples (list of data, type, r, g, b)
        self.init_data()


    def init_data(self, interval3D=None):
        self.data = []
        p_min = Point3D(5, 5, 5)
        p_max = Point3D(15, 15, 15)
        step = 2

        self.interval3D = gen.generate_interval3D(p_min, p_max, step) \
                                if not interval3D else interval3D

        #self.data = [(util.flat_segments(self.interval3D.segments), GL_LINES, 1, 1, 1)]

        convex_edges  = []
        concave_edges = []
        for s in self.interval3D.segments:
            edges = convex_edges if s.type == Edge3D.CONVEX else concave_edges
            edges.append(s)

        self.data.append((util.flat_segments(convex_edges ), GL_LINES, 1, 1, 1))
        self.data.append((util.flat_segments(concave_edges), GL_LINES, 1, 1, 0))

        # interval2Ds (projections of Interval3D)
        self.int2Ds = [self.interval3D.int_xz, self.interval3D.int_zy, self.interval3D.int_yx]
        for i in xrange(len(self.int2Ds)):
            self.int2Ds[i] = (util.flat_points(self.int2Ds[i].points), GL_LINE_LOOP, 1, 0, 0)


    def add_projections(self):
        if self.int2Ds not in self.data:
            self.data.extend(self.int2Ds)

    def remove_projections(self):
        for t in self.int2Ds:
            if t in self.data:
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


class Interval2D(object):

    def __init__(self, points=[], squares=[]):
        self.points = points
        self.squares = squares

    def __str__(self):
        return '\n'.join(' '.join(str(coord) for coord in p.get()) for p in self.points)

    def __contains__(self, point):
        if not isinstance(point, (Point2D, Point3D)):
            return False
        else:
            return self._contains_binary_search(point) if self.squares else \
                   self._contains_ray_throwing (point)


    def _contains_binary_search(self, point, imin=None, imax=None):
        imin = imin if imin else 0
        imax = imax if imax else len(self.squares)

        if imin >= imax:
            return False

        imid = (imin + imax) / 2
        low, high = self.squares[imid]

        if low.x() > point.x() or low.y() > point.y():      #left or down
            return self._contains_binary_search(point, imin, imid)
        elif high.x() < point.x() or high.y() < point.y():  # right or up
            return self._contains_binary_search(point, imid+1, imax)
        else: # inside
            return True


    def _contains_ray_throwing(self, point):
        # throw two rays horizontally in both ways
        # right_ray and left_ray tells if they cross an odd number of segments
        # we need both ways because there are some cases (e.g upper horizontal line)
        # where right_ray is odd and left_ray is zero
        sz = len(self.points)
        right_ray = left_ray = False
        for i in xrange(sz):
            p1, p2 = self.points[i], self.points[(i+1)%sz]

            if p1.y() <= point.y() <= p2.y() or \
               p1.y() >= point.y() >= p2.y():

                # test if point is in the line segment [p1, p2]
                if (p1.x() <= point.x() <= p2.x() or \
                    p1.x() >= point.x() >= p2.x()) and \
                   ((point.x()-p1.x())*(p2.y()-point.y()) == (p2.x()-point.x())*(point.y()-p1.y())):
                   return True

                if point.x() <= min((p1.x(), p2.x())):
                    right_ray = not right_ray
                if point.x() >= max((p1.x(), p2.x())):
                    left_ray = not left_ray

        return right_ray == left_ray and right_ray


class Interval3D(object):

    def __init__(self, segments=[],
                 int_xz=Interval2D(),
                 int_zy=Interval2D(),
                 int_yx=Interval2D()):
        self.segments = segments
        self.int_xz = int_xz
        self.int_zy = int_zy
        self.int_yx = int_yx

