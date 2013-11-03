#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


from OpenGL.GL import *     # types : GL_POINTS, GL_LINES, ...

import generation as gen
from geom import *
from path import *
import util

Ax = 7.5
Bx = 6.0

class Intervals(object):

    def __init__(self):
        self.data = []      # list of tuples (list of data, type, r, g, b)
        self.degenerate = False
        self.init_data()


    def init_data(self, interval3D=None):
        self.data = []
        p_min = Point3D(5, 5, 5)
        p_max = Point3D(15, 15, 15)
        step = 2

        # self.make_interval_2D(p_min, p_max, step)
        # self.make_interval_3D(p_min, p_max, step, interval3D)
        # self.path_stuff()
        self.extension_point_test()


    def make_interval_2D(self, p_min, p_max, step):
        self.interval2D = gen.generate_interval2D(p_min, p_max, step, True)

        int_3D_pts = [Point3D(p.x(), p.y(), 0) for p in self.interval2D.points]
        self.data.append((util.flat_points(int_3D_pts), GL_LINE_LOOP, 1, 0, 0))
        self.data.append((util.flat_points(int_3D_pts), GL_POINTS, 1, 1, 1))
        squares = []
        for s in self.interval2D.squares:
            squares.append(Point3D(s[0].x(), s[0].y(), 0))
            squares.append(Point3D(s[1].x(), s[1].y(), 0))
        self.data.append((util.flat_points(squares), GL_LINES, 1, 0, 1))
        self.int2Ds = []


    def make_interval_3D(self, p_min, p_max, step, interval3D=None):
        self.interval3D = gen.generate_interval3D(p_min, p_max, step, self.degenerate) \
                                if not interval3D else interval3D

        #self.data = [(util.flat_segments(self.interval3D.segments), GL_LINES, 1, 1, 1)]

        typed_edges = { Edge3D.CONVEX: [], Edge3D.CONCAVE1: [], Edge3D.CONCAVE2: [] }
        for s in self.interval3D.segments:
            typed_edges[s.type].append(s)

        # concave_edges = typed_edges[Edge3D.CONCAVE2]+typed_edges[Edge3D.CONCAVE1]
        # concave_edges = sorted(concave_edges, cmp=Edge3D.same_coordinates)
        # g = 0
        # for e in concave_edges:
        #     g += 1.0 / len(concave_edges)
        #     self.data.append(([e.a.get(),e.b.get()], GL_LINES, 1, g, 0))

        self.data.append((util.flat_segments(typed_edges[Edge3D.CONVEX]  ), GL_LINES, 1, 1, 1))
        self.data.append((util.flat_segments(typed_edges[Edge3D.CONCAVE1]), GL_LINES, 1, 1, 0))
        self.data.append((util.flat_segments(typed_edges[Edge3D.CONCAVE2]), GL_LINES, 1, 0, 1))
        # self.data.append((util.flat_points((p_min,p_max)), GL_POINTS, 1, 0, 0))

        #path_points = shortest_path_from_signature(p_min, p_max, typed_edges[Edge3D.CONCAVE2]+typed_edges[Edge3D.CONCAVE1])
        #self.data.append((util.flat_points(path_points), GL_LINE_STRIP, 1, 0, 0))

        # interval2Ds (projections of Interval3D)
        self.int2Ds = [self.interval3D.int_xy, self.interval3D.int_zx, self.interval3D.int_yz]
        for i in xrange(len(self.int2Ds)):
            self.int2Ds[i] = (util.flat_points(self.int2Ds[i].points), GL_LINE_LOOP, 1, 0, 0)


    def extension_point_test(self):
        A = Point3D(Ax, 0, 0)
        B = Point3D(Bx, 10, 10)

        signature = [ Edge3D(Point3D(0,  10, 10), Point3D(10, 10, 10)),
                      Edge3D(Point3D(5,  10, 20), Point3D(5,  20, 20)),
                      Edge3D(Point3D(10, 20, 25), Point3D(10, 20, 35)) ]

        s = Segment(A, B)
        path_segs = [s]
        path_pts = [A, B]
        e1 = signature[0]
        for e2 in signature[1:]:
            ext_point = compute_extension_point(s, e1, e2.asLineAxis3D())
            if not ext_point:
                print "failed to compute ext point at", s, e1, e2
                break
            s = Segment(B, ext_point)
            B = ext_point
            path_pts.append(s.b)
            path_segs.append(s)

        self.data.append((util.flat_segments(path_segs), GL_LINES, 1, 1, 0))
        self.data.append((util.flat_points(path_pts), GL_POINTS, 1, 1, 1))

        # self.data.append((util.flat_points((A,B)), GL_POINTS, 1, 1, 1))
        self.data.append((util.flat_segments(signature), GL_LINES, 1, 0, 0))

        # if ext_point:
        #     ext_path = Segment(B, ext_point)
        #     self.data.append((util.flat_segments((s,ext_path)), GL_LINES, 1, 1, 0))
        #     self.data.append((ext_point.get(), GL_POINTS, 0, 1, 1))
        #     print ext_point


    def path_stuff(self):
        l_list = []
        p_list = []
        l = LineAxis3D(10.0, 15.0, COORDINATES[0])
        s =  Segment(Point3D(-0.58, -1.69, -1.16), Point3D(2.05, 4.49, 4.5))
        e = Edge3D(Point3D(0.8, 4.49, 4.5), Point3D(2.8, 4.49, 4.5))

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

    def copy_2D(self, x, y):
        points = [Point2D(x(p), y(p)) for p in self.points]
        squares = [(Point2D(x(s[0]), y(s[0])), Point2D(x(s[1]), y(s[1]))) for s in self.squares]
        return Interval2D(points, squares)

    def _contains_binary_search(self, point, imin=None, imax=None):
        return -1 != self.find_square(point, imin, imax)


    def find_square(self, point, imin=None, imax=None):
        imin = imin if imin else 0
        imax = imax if imax else len(self.squares)

        if imin >= imax:
            return -1

        imid = (imin + imax) / 2
        low, high = self.squares[imid]

        if low.x() > point.x() or low.y() > point.y():      #left or down
            return self.find_square(point, imin, imid)
        elif high.x() < point.x() or high.y() < point.y():  # right or up
            return self.find_square(point, imid+1, imax)
        else: # inside
            return imid


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
                 int_xy=Interval2D(),
                 int_zx=Interval2D(),
                 int_yz=Interval2D()):
        self.segments = segments
        self.int_xy = int_xy
        self.int_zx = int_zx
        self.int_yz = int_yz


if __name__ == '__main__':
    Intervals()

