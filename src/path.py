#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '20-07-2013'


from interval import *


def visible(interval, p, q):
    if  isinstance(interval, Interval2D):
        return _visible_2D(interval, p, q)
    elif isinstance(interval, Interval3D):
        return _visible_3D(interval, p, q)
    else:
        return False


def _visible_2D(interval, p, q):
    i = interval.find_square(p)
    j = interval.find_square(q)

    if i == -1 or j == -1:
        return False
    elif i == j:
        return True

    if i > j:
        i, j = j, i

    s = Segment(p,q)
    for n in xrange(i, j):
        s1 = interval.squares[n  ]
        s2 = interval.squares[n+1]
        if not s.does_intersect(Segment(s1[1], s2[0])):
            return False

    return True


def _visible_3D(interval, p, q):
    vis_xy = _visible_2D(interval.int_xy, p, q)
    vis_zx = _visible_2D(interval.int_zx.copy_2D(Point3D.z, Point3D.x), p, q)
    vis_yz = _visible_2D(interval.int_yz.copy_2D(Point3D.y, Point3D.z), p, q)
    return vis_xy and vis_zx and vis_yz

