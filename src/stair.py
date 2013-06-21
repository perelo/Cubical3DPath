#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


from OpenGL.GL import *     # types : GL_POINTS, GL_LINES, ...
from geom import *
import util


class StairModel:

    def __init__(self):
        self.data = []      # list of tuples (list of data, type, r, g, b)
        self.init_data()


    def init_data(self):
        #self.l_reconstructed()

        self.data = [(util.flat_points(stair), GL_LINE_LOOP, 1, 0, 0)
                            for stair in StairModel.gen_3_intervals(1, 1, 11, 11, 1)]


    def read_file(self, name):
        f = open(name, 'r')
        size = f.readline()
        size = int(size.split()[1])
        f.readline()    # XY_POLYGON
        f.readline()    # X MIN_Y MAX_T

        array = []
        for i in range(size):
            l = f.readline()
            s = l.split()
            array.append((int(s[0]), int(s[1]), int(s[2])))
        f.close()

        lower_line = [Point3D(x, min_y, 0) for x, min_y, max_y in array]
        upper_line = [Point3D(x, max_y, 0) for x, min_y, max_y in array]
        upper_line.reverse()
        lower_line.extend(upper_line)
        return lower_line


    def l_reconstructed(self):
        raw_squel = [
                 Segment3D(Point3D( 5, 5, 5), Point3D( 5, 5,10)),
                 Segment3D(Point3D( 5, 5, 5), Point3D(15, 5, 5)),
                 Segment3D(Point3D( 5, 5,10), Point3D(15, 5,10)),
                 Segment3D(Point3D(15, 5, 5), Point3D(15, 5,10)),

                 Segment3D(Point3D( 5,10, 5), Point3D( 5,10,10)),
                 Segment3D(Point3D( 5,10, 5), Point3D(10,10, 5)),
                 Segment3D(Point3D( 5,10,10), Point3D(10,10,10)),

                 Segment3D(Point3D( 5, 5, 5), Point3D( 5,10, 5)),
                 Segment3D(Point3D( 5, 5,10), Point3D( 5,10,10)),

                 Segment3D(Point3D(10,10, 5), Point3D(10,20, 5)),
                 Segment3D(Point3D(10,10,10), Point3D(10,20,10)),

                 Segment3D(Point3D(15, 5, 5), Point3D(15,20, 5)),
                 Segment3D(Point3D(15, 5,10), Point3D(15,20,10)),

                 Segment3D(Point3D(10,20, 5), Point3D(15,20, 5)),
                 Segment3D(Point3D(15,20, 5), Point3D(15,20,10)),
                 Segment3D(Point3D(15,20,10), Point3D(10,20,10)),
                 Segment3D(Point3D(10,20,10), Point3D(10,20, 5)),


                 #(10,10,10), (20,10,10), (10,20,10), (20,20,10),
                 #(10,10,20), (20,10,20), (10,20,20), (20,20,20),
                 #(10,10,10), (10,10,20), (20,10,10), (20,10,20),
                 #(10,20,10), (10,20,20), (20,20,10), (20,20,20),
                 #(10,10,10), (10,20,10), (10,10,20), (10,20,20),
                 #(20,10,10), (20,20,10), (20,10,20), (20,20,20),
              ]

        flat_squel = util.flat_segments(raw_squel)
        projxy = set([Segment3D(Point3D(s.a.x(), s.a.y(), 0), Point3D(s.b.x(), s.b.y(), 0)) \
                                        for s in raw_squel if ((s.a.x(), s.a.y()) != (s.b.x(), s.b.y()))])
        projxz = set([Segment3D(Point3D(s.a.x(), 0, s.a.z()), Point3D(s.b.x(), 0, s.b.z())) \
                                        for s in raw_squel if ((s.a.x(), s.a.z()) != (s.b.x(), s.b.z()))])
        projyz = set([Segment3D(Point3D(0, s.a.y(), s.a.z()), Point3D(0, s.b.y(), s.b.z())) \
                                        for s in raw_squel if ((s.a.y(), s.a.z()) != (s.b.y(), s.b.z()))])

        flat_projxy = util.flat_segments(projxy)
        flat_projxz = util.flat_segments(projxz)
        flat_projyz = util.flat_segments(projyz)

        self.reconstruct_pts = self.reconstruct_points(flat_projxy, flat_projxz, flat_projyz)
        reconstruct_seg = self.reconstruct_segments(projxy, projxz, projyz)


        # append arrays to data
        self.data.append((flat_projxy, GL_LINES, 1, 0, 0))
        self.data.append((flat_projxz, GL_LINES, 1, 0, 0))
        self.data.append((flat_projyz, GL_LINES, 1, 0, 0))

        self.data.append((reconstruct_seg, GL_LINES, 1, 1, 1))


    def reconstruct_segments(self, projxy, projxz, projyz):
        result_set = set()
        for x1, y1, z1 in self.reconstruct_pts:
            for x2, y2, z2 in self.reconstruct_pts:
                if (x1, y1, z1) != (x2, y2, z2) and \
                   ((x1 != x2 and y1 == y2 and z1 == z2) or
                    (x1 == x2 and y1 != y2 and z1 == z2) or
                    (x1 == x2 and y1 == y2 and z1 != z2)):
                    result_set.add(Segment3D(Point3D(x1, y1, z1), Point3D(x2, y2, z2)))
        return [(x, y, z) for s in result_set for x, y, z in (s.a.coordinates, s.b.coordinates)]


    def reconstruct_points(self, projxy, projxz, projyz):
        reconstruct_set = set()

        zero = 0
        for x_xy, y_xy, zero in projxy:
            for x_xz, zero, z_xz in projxz:
                if x_xy == x_xz:
                    for zero, y_yz, z_yz in projyz:
                        if y_xy == y_yz and z_xz == z_yz:
                            reconstruct_set.add((x_xy, y_yz, z_xz))
        #self.reconstruct = list(reconstruct_set)
        return reconstruct_set
        #print len(self.reconstruct)


    @staticmethod
    def gen_3_intervals(xMin, yMin, xMax, yMax, step_size = 1):
        stairxy = StairModel.generate_interval2D(xMin, yMin, xMax, yMax, step_size)
        stairxz = StairModel.generate_interval2D(xMin, yMin, xMax, yMax, step_size)
        stairyz = StairModel.generate_interval2D(xMin, yMin, xMax, yMax, step_size)

        stairxy = [Point3D(p2D.x(), p2D.y(), 0) for p2D in stairxy]
        stairxz = [Point3D(p2D.y(), 0, p2D.x()) for p2D in stairxz]
        stairyz = [Point3D(0, p2D.y(), p2D.x()) for p2D in stairyz]

        return [stairxy, stairxz, stairyz]


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


