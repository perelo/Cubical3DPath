#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '17-06-2013'


from geom import *


class StairModel:

    def __init__(self):
        self.squel = [
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

        self.flat_squel = [(x, y, z) for s in self.squel for x, y, z in s.flat()]
        self.projxy = set([Segment3D(Point3D(s.a.x(), s.a.y(), 0), Point3D(s.b.x(), s.b.y(), 0)) \
                                        for s in self.squel if ((s.a.x(), s.a.y()) != (s.b.x(), s.b.y()))])
        self.projxz = set([Segment3D(Point3D(s.a.x(), 0, s.a.z()), Point3D(s.b.x(), 0, s.b.z())) \
                                        for s in self.squel if ((s.a.x(), s.a.z()) != (s.b.x(), s.b.z()))])
        self.projyz = set([Segment3D(Point3D(0, s.a.y(), s.a.z()), Point3D(0, s.b.y(), s.b.z())) \
                                        for s in self.squel if ((s.a.y(), s.a.z()) != (s.b.y(), s.b.z()))])

        #print 'projxy =', len(self.projxy), self.projxy, '\n'
        #print 'projxz =', len(self.projxz), self.projxz, '\n'
        #print 'projyz =', len(self.projyz), self.projyz

        self.flat_projxy = [(x, y, z) for s in self.projxy for x, y, z in s.flat()]
        self.flat_projxz = [(x, y, z) for s in self.projxz for x, y, z in s.flat()]
        self.flat_projyz = [(x, y, z) for s in self.projyz for x, y, z in s.flat()]

        self.reconstruct_pts = self.reconstruct_points(self.flat_projxy, self.flat_projxz, self.flat_projyz)
        self.reconstruct_seg = self.reconstruct_segments(self.projxy, self.projxz, self.projyz)


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


    def gen_3_stairs(self):
        """ Generate three couple of monoton chains on the planes
        """
        array = []

        # On (xy) plane
        lower_line = generate_stair2D(10, 10, 30, 30, True, 10)
        upper_line = generate_stair2D(10, 10, 30, 30, False, 10)
        upper_line.reverse()
        array = lower_line[1:]
        array.extend(upper_line[1:])
        stairxy = [(x, y, 0) for x, y in array]

        # On (xz) plane
        lower_line = stair.generate_stair2D(10, 10, 30, 30, True, 10)
        upper_line = stair.generate_stair2D(10, 10, 30, 30, False, 10)
        upper_line.reverse()
        array = lower_line[1:]
        array.extend(upper_line[1:])
        stairxz = [(x, 0, z) for x, z in array]

        # On (yz) plane
        lower_line = stair.generate_stair2D(10, 10, 30, 30, True, 10)
        upper_line = stair.generate_stair2D(10, 10, 30, 30, False, 10)
        upper_line.reverse()
        array = lower_line[1:]
        array.extend(upper_line[1:])
        stairyz = [(0, y, z) for y, z in array]

        return (stairxy, stairxz, stairyz)


    @staticmethod
    def generate_stair2D(xMin, yMin, xMax, yMax, n = None, start_horiz = False):
        """ Generate a list of m couples (n <= m <= n*2) as 2D points,
            joined together forming monotonically increasing rectiligne function
            starting from (xMin, yMin), ending at (xMax, yMax).
            start_horiz specifies the direction of the first "segment".
            if n isn't provided, it will be set as random.randint(0, 10)
        """
        import random
        if not n:
            n = random.randint(0, 10)

        pointsX = random.sample(range(xMin, xMax), n)
        pointsY = random.sample(range(yMin, yMax), n)
        pointsX.sort()
        pointsY.sort()
        points = zip(pointsX, pointsY)
        points.insert(0, (xMin, yMin))
        points.append((xMax, yMax))

        return rectilinize(points, start_horiz)


    @staticmethod
    def rectilinize(points, start_horiz):
        """ Return the given list of points on which we have added new points
            so the graph formed by the line segments between consecutive points
            is formed by just horizontal and vertical line segments
        """
        result = []
        for i in range(len(points)-1):
            result.append(points[i])
            if start_horiz and points[i][1] != points[i+1][1]:
                result.append((points[i+1][0], points[i][1]))
            elif not start_horiz and points[i][0] != points[i+1][0]:
                result.append((points[i][0], points[i+1][1]))
            start_horiz = not start_horiz
        result.append(points[-1])
        return result

