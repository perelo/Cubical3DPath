#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '20-07-2013'


from interval import *


NO_CHAIN    = 0
LOWER_CHAIN = 1 << 0
UPPER_CHAIN = 1 << 1
ALL_CHAINS  = UPPER_CHAIN | LOWER_CHAIN


def visibility(interval, p, q):
    f = lambda i, p, q: False
    d = dict(((Interval2D, _visibility_2D),
              (Interval3D, _visibility_3D)))
    return d.get(type(interval), f)(interval, p, q)


def _visibility_2D(interval, p, q):
    if isinstance(p, (Point2D, Point3D)):
        if isinstance(q, (Point2D, Point3D)):
            return _visibility_2D_point_point(interval, p, q)
        else:
            return _visibility_2D_point_segment(interval, p, q)
    else:
        return _visibility_2D_segment_segment(interval, p, q)


def _visibility_2D_point_point(interval, p, q):
    mask = NO_CHAIN
    if interval.find_square(p) == interval.find_square(q):
        return mask

    i = 1
    segments = []
    # add vertical segments of lower and upper_line to be tested w/ intersection
    # when a.y() < b.y(), it's on lower_line, else it's on upper_line
    while i < len(interval.points)-1:
        segments.append(Segment(interval.points[i], interval.points[i+1]))
        i += 2

    line_pq = Segment(p,q).asLine()
    for s in segments:
        p = line_pq.intersection(s)
        if p is not None:
            mask |= LOWER_CHAIN if s.a.y() < s.b.y() else UPPER_CHAIN

    return mask


def _visibility_2D_point_segment(interval, p, s):
    pass


def _visibility_2D_segment_segment(interval, s1, s2):
    pass


def _visibility_3D(interval, p, q):
    zx = (Point3D.z, Point3D.x)
    yz = (Point3D.y, Point3D.z)
    vis_xy = _visible_2D(interval.int_xy, p, q)
    vis_zx = _visible_2D(interval.int_zx.copy_2D(*zx), p.copy_2D(*zx), q.copy_2D(*zx))
    vis_yz = _visible_2D(interval.int_yz.copy_2D(*yz), p.copy_2D(*yz), q.copy_2D(*yz))
    return vis_xy and vis_zx and vis_yz

