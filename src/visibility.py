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

EPSILON = 0.01


def visibility(interval, p, q):
    d = { Interval2D: _visibility_2D,
          Interval3D: _visibility_3D }
    f = lambda i, p, q: False   # if interval's type is crap, return False
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
        if interval.points[i+1] != interval.squares[-1][1]: # don't add the rightmost segment
            segments.append(Segment(interval.points[i], interval.points[i+1]))
        i += 2

    seg_pq = Segment(p,q)
    line_pq = seg_pq.asLine2D()
    for s in segments:
        p = line_pq.intersection(s)
        if p is not None and p.is_in_rectangle(seg_pq, True):
            mask |= LOWER_CHAIN if s.a.y() < s.b.y() else UPPER_CHAIN

    return mask


def _visibility_2D_point_segment_old(interval, p, s):
    """
        find upper and lower visibility on s relative to p
        return the visible sub segment or None
        everything must be inside interval
        /!\ Linear method /!\
    """

    # determine the orientation of s
    x, y = Point2D.x, Point2D.y
    create_point = lambda x, y: Point2D(x, y)
    if s.a.y() == s.b.y():
        x, y = y, x
        create_point = lambda x, y: Point2D(y, x)

    # force s to be increasing
    if y(s.a) > y(s.b):
        s.a, s.b = s.b, s.a

    p_min = p_max = None

    # first, check if both end points of s are visible
    if _visibility_2D_point_point(interval, p, s.a) == 0:
        p_min = s.a
    if _visibility_2D_point_point(interval, p, s.b) == 0:
        p_max = s.b

    # if one of the end point isn't visible,
    # iterate through the steps of the interval
    # and compute the intersection and visibility
    # to determine the visibility boundaries
    if p_min is None or p_max is None:
        steps_pts = interval.points[2::2]
        steps_pts.remove(interval.squares[-1][1]) # remove top right point
        for step in steps_pts:
            seg = Segment(p, step)
            inter = seg.asLine2D().intersection(s, True)
            if inter and _visibility_2D_point_point(interval, p, inter) == 0:
                if p_min is None or y(inter) < y(p_min):
                    p_min = inter
                if p_max is None or y(inter) > y(p_max):
                    p_max = inter

    return Segment(p_min, p_max) if p_min and p_max else None


def _visibility_2D_point_segment(interval, p, s):
    """
        find upper and lower visibility on s relative to p
        return the visible sub segment or None
        everything must be inside interval
        /!\ Binary search method /!\
    """
    p_min = p_max = None

    # determine the orientation of s
    x, y = Point2D.x, Point2D.y
    if s.a.y() == s.b.y():
        x, y = y, x

    # force s to be increasing
    if y(s.a) > y(s.b):
        s.a, s.b = s.b, s.a

    vis = None
    _find_bound.upper = _find_bound.lower = None
    # first, check if both end points of s are visible
    if _visibility_2D_point_point(interval, p, s.a) == 0:
        p_min = s.a
    else:
        vis = _find_bound(LOWER_BOUND, interval, p, s, y)
        p_min = _find_bound.lower

    if _visibility_2D_point_point(interval, p, s.b) == 0:
        p_max = s.b
    else:
        vis = _find_bound(UPPER_BOUND, interval, p, s, y)
        p_max = _find_bound.upper

    return Segment(p_min, p_max) if p_min and p_max else vis


UPPER_BOUND = 0
LOWER_BOUND = 1
def _find_bound(bound, interval, p, s, y):
    mid = s.middle()
    vis = _visibility_2D_point_point(interval, p, mid)

    if y(s.a)+EPSILON >= y(s.b):
        return vis

    if vis & LOWER_CHAIN != 0:
         _find_bound(bound, interval, p, Segment(mid, s.b), y)
    elif vis & UPPER_CHAIN != 0:
         _find_bound(bound, interval, p, Segment(s.a, mid), y)
    elif vis == 0: # visible
        if bound == LOWER_BOUND:
            _find_bound.lower = mid
            _find_bound(bound, interval, p, Segment(s.a, mid), y)
        else:
            _find_bound.upper = mid
            _find_bound(bound, interval, p, Segment(mid, s.b), y)

def _visibility_2D_segment_segment(interval, p, q):
    return False

def _visibility_3D(interval, p, q):
    zx = (Point3D.z, Point3D.x)
    yz = (Point3D.y, Point3D.z)
    vis_xy = _visible_2D(interval.int_xy, p, q)
    vis_zx = _visible_2D(interval.int_zx.copy_2D(*zx), p.copy_2D(*zx), q.copy_2D(*zx))
    vis_yz = _visible_2D(interval.int_yz.copy_2D(*yz), p.copy_2D(*yz), q.copy_2D(*yz))
    return vis_xy and vis_zx and vis_yz

