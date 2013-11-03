#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '29-07-2013'


from math import sqrt

import operator
from geom import *


def shortest_path_from_signature(start, edges):
    if len(edges) == 0:
        return (start, end)

    first = edges[0].a.returnCopy()
    first.get()[edges[0].orientation()] += 1

    path = [start, first]
    for i in xrange(0, len(edges)-1):
        s = Segment(path[-1],path[-2])
        l = edges[i+1].asLineAxis3D()
        p = compute_extension_point(s, edges[i], l)
        print p
        path.append(p)

    path.append(end)
    return path


def extend_path_over_signatures(s, edges):
    """
        Extend the path over the signatures given by edges.
        s is the first segment of the path
        s.b must be on edges[0]
    """
    path = [s]
    e1 = edges[0]
    for e2 in edges[1:]:
        next_point = compute_extension_point(s, e1, e2.asLineAxis3D())
        if not next_point or next_point not in e2:
            print "failed to compute next point at", s, e1, e2
            break
        s = Segment(B, next_point)
        B = next_point
        path.append(s)
    return path


def compute_extension_point(s, e, l):
    """
        Compute the point on l (LineAxis3D) that is the extension of the path
        in which the last segment is s and s.b is on e (Edge3D)
    """
    print "A =", s.a.get()
    print "B =", s.b.get()
    print "E =", e.a.get(), e.orientation()
    print "D =", l.get(), l.orientation

    # get the common unvariant axis between l and e
    nb_common_unvariant_axis = 0
    for d in range(3):      # d like dimension
        if d != l.orientation and e.a.get()[d] == e.b.get()[d]:
            common_unvariant_axis = d
            nb_common_unvariant_axis += 1

    if nb_common_unvariant_axis > 1:    # they have the same orientation
        print "same orientation"
        # TODO do something
        return

    # now, compute the point of the line described by s which is at the first
    # coordinate of l and compare one of it's other coordinate with the second
    # coordinate of l (the corresponding one). All this to determine if
    # the bending won't go concavely or up to infinity

    # coord_of_i are the coord represented by l.get[x] depending on l's orientation
    coord_of_0 = ( 1, 0, 0 )[l.orientation]     # y, x, x
    coord_of_1 = ( Point3D.z, Point3D.z, Point3D.y )[l.orientation]
    comparator = ( operator.gt, operator.lt, operator.gt )[common_unvariant_axis]

    a = s.asLine3D().point_at(l.get()[0], coord_of_0)
    if not a or comparator(coord_of_1(a), l.get()[1]):
        print "cannot bend"
        # return      # we would bend concavely or up to infinty...

    # Ok! now we can compute the damn extension point
    # and at the end check if we havn't bent too much (this is TODO)

    vect_coords = ( Vector3D.x, Vector3D.y, Vector3D.z )
    pts_coords = ( Point3D.x, Point3D.y, Point3D.z )

    # 't' means the axis to get depending on e and l orientation
    l_t      = dict(zip(COORDINATES,  pts_coords))[l.orientation  ]
    u_t_vect = dict(zip(COORDINATES, vect_coords))[e.orientation()]
    u_t_pt   = dict(zip(COORDINATES,  pts_coords))[e.orientation()]
    l_t_i    = dict(zip(COORDINATES, ( 0, 0, 1 )))[e.orientation()]

    u = Vector3D.vector_from_two_points(s.a, s.b).normalized()
    print "U =", u
    print l.coord_points[2](s.a), "+ sqrt( ((",l.get()[l_t_i], "-", u_t_pt(s.a), ")/", u_t_vect(u),")**2 - (",l.get()[0] ,"-", l.coord_points[0](s.a), ")**2 - (",l.get()[1] ,"-", l.coord_points[1](s.a), ")**2 )"
    r_t = l.coord_points[2](s.a) + sqrt( ((l.get()[l_t_i] - u_t_pt(s.a)) / u_t_vect(u))**2
                                        - (l.get()[0] - l.coord_points[0](s.a))**2
                                        - (l.get()[1] - l.coord_points[1](s.a))**2 )

    if r_t < l_t(s.b):
        print "bent too much!"
        # return

    return l.create_point(l.get()[0], l.get()[1], r_t)

