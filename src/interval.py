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
        self.intervals = []
        self.init_data()


    def init_data(self, intervals = None):
        #self.l_reconstructed()

        self.intervals = Interval.gen_3_intervals(5, 5, 15, 15, 1) \
                                            if intervals is None \
                                            else intervals

        flat_intervals = [util.flat_points(interval) for interval in self.intervals]
        self.data = [(interval, GL_LINE_LOOP, 1, 0, 0)
                            for interval in flat_intervals]

        points_3d = Interval.points3d_from_projection(Point3D(5, 5, 5), Point3D(15, 15, 15), *self.intervals)
        segments = Interval.extract_skeleton(points_3d, 1)

        self.data.append((util.flat_segments(segments), GL_LINES, 0, 0, 1))
        #self.data.append((util.flat_points(points_3d), GL_POINTS, 1, 1, 1))


    @staticmethod
    def extract_skeleton(points, step):
        skeleton = []

        get_zyx = lambda p: (p.z(), p.y(), p.x())
        get_xyz = lambda p: (p.x(), p.y(), p.z())
        get_zxy = lambda p: (p.z(), p.x(), p.y())

        create_point_xyz = lambda x, y, z: Point3D(x, y, z)
        skeleton.extend(Interval.get_edges(sorted(points, key=get_zyx), step,
                                           Point3D.x, Point3D.y, Point3D.z, create_point_xyz))

        create_point_zyx = lambda x, y, z: Point3D(z, y, x)
        skeleton.extend(Interval.get_edges(sorted(points, key=get_xyz), step,
                                           Point3D.z, Point3D.y, Point3D.x, create_point_zyx))

        create_point_yxz = lambda x, y, z: Point3D(y, x, z)
        skeleton.extend(Interval.get_edges(sorted(points, key=get_zxy), step,
                                           Point3D.y, Point3D.x, Point3D.z, create_point_yxz))

        return skeleton


    @staticmethod
    def get_edges(points, step, x, y, z, create_point):
        edges = [] # unitary edges

        y_ref = y(points[0])
        z_ref = z(points[0])
        for i in range(0, len(points)-1):
            p = points[i  ]
            q = points[i+1]

            if y(q) != y_ref or z(q) != z_ref:
                y_ref = y(q)
                z_ref = z(q)
                continue

            if Interval.is_eligible(points, p, step, x, y, z, create_point) or \
               Interval.is_eligible(points, q, step, x, y, z, create_point):
                edges.append((i, i+1))

        return [Segment3D(points[a], points[b]) for a, b in edges]


    @staticmethod
    def is_eligible(points, p, step, x, y, z, create_point):
            up    = create_point(x(p), y(p)+1, z(p)  ) in points
            down  = create_point(x(p), y(p)-1, z(p)  ) in points
            front = create_point(x(p), y(p)  , z(p)+1) in points
            back  = create_point(x(p), y(p)  , z(p)-1) in points

            if (up and down) or (front and back):
                # detect convex edges
                up_back    = create_point(x(p), y(p)+1, z(p)-1) in points
                down_front = create_point(x(p), y(p)-1, z(p)+1) in points
                return up and down and ((back and not up_back) or (front and not down_front))

            return True


    @staticmethod
    def points3d_from_projection(p_min, p_max, xy, xz, yz):
        step = 1
        points3d = []
        for x in np.arange(p_min.x(), p_max.x() + step, step):
            for y in np.arange(p_min.y(), p_max.y() + step, step):
                for z in np.arange(p_min.z(), p_max.z() + step, step):
                    p = Point3D(x, y, z)
                    if Interval.is_in(p, xy, Point3D.x, Point3D.y) and \
                       Interval.is_in(p, xz, Point3D.z, Point3D.x) and \
                       Interval.is_in(p, yz, Point3D.z, Point3D.y):
                        points3d.append(p)

        return points3d


    @staticmethod
    def is_in(point, polygon, x, y, close = True):
        # throw two rays horizontally in both ways
        # right_ray and left_ray tells if they cross an odd number of segments
        # we need both ways because there are some cases (e.g upper horizontal line)
        # where right_ray is odd and left_ray is zero
        sz = len(polygon)
        right_ray = left_ray = False
        for i in range(sz):
            p1, p2 = polygon[i], polygon[(i+1)%sz]

            if y(p1) <= y(point) <= y(p2) or \
               y(p1) >= y(point) >= y(p2):

                if close:
                    # test if point is in the line segment [p1, p2]
                    if (x(p1) <= x(point) <= x(p2) or \
                        x(p1) >= x(point) >= x(p2)) and \
                       ((x(point)-x(p1))*(y(p2)-y(point)) == (x(p2)-x(point))*(y(point)-y(p1))):
                       return True

                if x(point) <= min((x(p1), x(p2))):
                    right_ray = not right_ray
                if x(point) >= max((x(p1), x(p2))):
                    left_ray = not left_ray

        return right_ray == left_ray and right_ray


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

