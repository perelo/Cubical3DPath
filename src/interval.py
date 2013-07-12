#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


from OpenGL.GL import *     # types : GL_POINTS, GL_LINES, ...
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

        self.interval3D = Interval3D.generate_random_3D(p_min, p_max, step) \
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


    @staticmethod
    def generate_random_2D(p_min, p_max, step):
        from random import randrange

        xMin = p_min.x()
        yMin = p_min.y()
        xMax = p_max.x()
        yMax = p_max.y()

        if xMin >= xMax or yMin >= yMax:
            return []

        lower_line = [Point2D(xMin, yMin)]
        upper_line = [Point2D(xMin, randrange(yMin+step, yMax+step, step))]

        old_low  = lower_line[0].y()
        old_high = upper_line[0].y()

        # iterate through x with a defined step
        # for each step, pick a low and a high y coordinate
        # for lower and higher line respectively. Pick them right!
        lower_line_done = upper_line_done = False
        for i in range(xMin+step, xMax, step):
            if not lower_line_done:
                # min: old_low to keep lower_line going up
                # max: old_high+step to prevent vertical overlap
                low = randrange(old_low, old_high+step, step)
                if low >= yMax:
                    lower_line_done = True
                elif old_low < low: # old_low cannot be greater than low
                    # add points to make the lower_line rectilinear
                    lower_line.append(Point2D(i, old_low))
                    lower_line.append(Point2D(i, low))
                    old_low = low

            if not upper_line_done:
                # min: low to prevent crossing + inc to prevent horizontal overlap
                # max: yMax+step to reach yMax but not go further
                inc = step if not lower_line_done else 0
                high = randrange(max(low+inc, old_high), yMax+step, step)
                if old_high < high:
                    # add points to make the upper_line rectilinear
                    upper_line.append(Point2D(i, old_high))
                    upper_line.append(Point2D(i, high))
                    old_high = high
                if high >= yMax:
                    upper_line_done = True

        upper_line.append(Point2D(xMax, yMax))
        lower_line.append(Point2D(xMax, old_low))

        upper_line.reverse()
        lower_line.extend(upper_line)
        return Interval2D(lower_line)


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


    @staticmethod
    def generate_random_3D(p_min, p_max, step):
        # generate three random 2D intervals
        xy = Interval2D.generate_random_2D(p_min, p_max, step)
        xz = Interval2D.generate_random_2D(p_min, p_max, step)
        yz = Interval2D.generate_random_2D(p_min, p_max, step)

        # convert in 3D as projections
        xy = [Point3D(p2D.x(), p2D.y(), 0) for p2D in xy.points]
        xz = [Point3D(p2D.y(), 0, p2D.x()) for p2D in xz.points]
        yz = [Point3D(0, p2D.y(), p2D.x()) for p2D in yz.points]

        # reconstruct the volume
        points = Interval3D._points3d_from_projection(p_min, p_max, xy, xz, yz, step)
        segments = Interval3D._extract_skeleton(points, step)
        return Interval3D(segments)


    @staticmethod
    def _points3d_from_projection(p_min, p_max, xy, xz, yz, step):
        points = []
        for x in range(p_min.x(), p_max.x() + step, step):
            for y in range(p_min.y(), p_max.y() + step, step):
                for z in range(p_min.z(), p_max.z() + step, step):
                    p = Point3D(x, y, z)
                    if Interval3D._is_in(p, xy, Point3D.x, Point3D.y) and \
                       Interval3D._is_in(p, xz, Point3D.z, Point3D.x) and \
                       Interval3D._is_in(p, yz, Point3D.z, Point3D.y):
                        points.append(p)

        return points


    @staticmethod
    def _extract_skeleton(points, step):
        skeleton = []

        get_zyx = lambda p: (p.z(), p.y(), p.x())
        get_xyz = lambda p: (p.x(), p.y(), p.z())
        get_zxy = lambda p: (p.z(), p.x(), p.y())

        create_point_xyz = lambda x, y, z: Point3D(x, y, z)
        skeleton.extend(Interval3D._get_edges(sorted(points, key=get_zyx), step,
                                           Point3D.x, Point3D.y, Point3D.z, create_point_xyz))

        create_point_zyx = lambda x, y, z: Point3D(z, y, x)
        skeleton.extend(Interval3D._get_edges(sorted(points, key=get_xyz), step,
                                           Point3D.z, Point3D.y, Point3D.x, create_point_zyx))

        create_point_yxz = lambda x, y, z: Point3D(y, x, z)
        skeleton.extend(Interval3D._get_edges(sorted(points, key=get_zxy), step,
                                           Point3D.y, Point3D.x, Point3D.z, create_point_yxz))

        return skeleton


    @staticmethod
    def _get_edges(points, step, x, y, z, create_point):
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

            if Interval3D._edge_eligible(points, (p,q), step, x, y, z, create_point):
                edges.append((i, i+1))

        edges = Interval3D._extend_adjacent_edges([(points[a], points[b]) for a, b in edges])
        return [Segment3D(p, q) for p, q in edges]


    @staticmethod
    def _edge_eligible(points, e, step, x, y, z, create_point, first=True):
        p, q = e
        p_up    = create_point(x(p), y(p)+step, z(p)     ) in points
        p_down  = create_point(x(p), y(p)-step, z(p)     ) in points
        p_front = create_point(x(p), y(p)  ,    z(p)+step) in points
        p_back  = create_point(x(p), y(p)  ,    z(p)-step) in points
        q_up    = create_point(x(q), y(q)+step, z(q)     ) in points
        q_down  = create_point(x(q), y(q)-step, z(q)     ) in points
        q_front = create_point(x(q), y(q)  ,    z(q)+step) in points
        q_back  = create_point(x(q), y(q)  ,    z(q)-step) in points

        if (p_up and p_down) or (p_front and p_back) or \
           (q_up and q_down) or (q_front and q_back):
            # check for concaveness

            p_up_back    = create_point(x(p), y(p)+step, z(p)-step) in points
            p_up_front   = create_point(x(p), y(p)+step, z(p)+step) in points
            p_down_front = create_point(x(p), y(p)-step, z(p)+step) in points
            p_down_back  = create_point(x(p), y(p)-step, z(p)-step) in points
            q_up_back    = create_point(x(q), y(q)+step, z(q)-step) in points
            q_up_front   = create_point(x(q), y(q)+step, z(q)+step) in points
            q_down_front = create_point(x(q), y(q)-step, z(q)+step) in points
            q_down_back  = create_point(x(q), y(q)-step, z(q)-step) in points

            if (p_up and p_down) and (q_up and q_down):
                return (p_back  and q_back  and not p_up_back    and not q_up_back) or \
                       (p_front and q_front and not p_down_front and not q_down_front)

            elif (p_front and p_back) and (q_front and q_back):
                return (p_up   and q_up   and not p_up_back    and not q_up_back) or \
                       (p_down and q_down and not p_down_front and not q_down_front)

        # convex
        return True


    @staticmethod
    def _extend_adjacent_edges(edges):
        merged_edges = []
        first = ()
        streak = False
        for i in range(len(edges)-1):
            e1 = edges[i  ]
            e2 = edges[i+1]
            if e1[1] == e2[0]:
                if not streak:
                    first = e1
                    streak = True
            else:
                merged_edges.append((first[0], e1[1]) if streak else e1)
                streak = False

        merged_edges.append((first[0], edges[-1][1]) if streak else edges[-1])
        return merged_edges


    @staticmethod
    def _is_in(point, polygon, x, y, close = True):
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

