#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module for generating 2D and 3D intervals
"""

__author__ = 'Eloi Perdereau'
__date__ = '12-07-2013'


from random import randrange

from geom import *
import interval


def generate_interval2D(p_min, p_max, step):
    xMin = p_min.x()
    yMin = p_min.y()
    xMax = p_max.x()
    yMax = p_max.y()

    if xMin >= xMax or yMin >= yMax:
        return []

    lower_line = [Point2D(xMin, yMin)]
    upper_line = [Point2D(xMin, randrange(yMin+step, yMax+step, step))]

    # list of tuples representing "squares" within the interval
    # they are used to find in O(log(n)) if a point is inside the interval
    squares = []

    square_low = p_min      # bottom left point of current square
    square_up  = None       # upper right point of current square

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
                square_up = Point2D(i, old_high)
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
                square_up = Point2D(i, old_high)
                old_high = high
            if high >= yMax:
                upper_line_done = True

        if square_up:
            squares.append((square_low,square_up))
            square_low = Point2D(i, old_low)
            square_up = None

    squares.append((square_low, p_max))

    upper_line.append(Point2D(xMax, yMax))
    lower_line.append(Point2D(xMax, old_low))

    upper_line.reverse()
    lower_line.extend(upper_line)
    return interval.Interval2D(lower_line, squares)


def generate_interval3D(p_min, p_max, step):
    # generate three random 2D intervals
    xy = generate_interval2D(p_min, p_max, step)
    xz = generate_interval2D(p_min, p_max, step)
    yz = generate_interval2D(p_min, p_max, step)

    # reconstruct the volume
    points = _points3d_from_intervals2D(p_min, p_max, xy, xz, yz, step)
    segments = _extract_skeleton(points, step)
    return interval.Interval3D(segments)


def _points3d_from_intervals2D(p_min, p_max, xy, xz, yz, step):
    points = []
    for x in range(p_min.x(), p_max.x() + step, step):
        for y in range(p_min.y(), p_max.y() + step, step):
            for z in range(p_min.z(), p_max.z() + step, step):
                if Point2D(x, y) in xy and \
                   Point2D(x, z) in xz and \
                   Point2D(y, z) in xz:
                    points.append(Point3D(x, y, z))

    return points


def _extract_skeleton(points, step):
    skeleton = []

    get_zyx = lambda p: (p.z(), p.y(), p.x())
    get_xyz = lambda p: (p.x(), p.y(), p.z())
    get_zxy = lambda p: (p.z(), p.x(), p.y())

    create_point_xyz = lambda x, y, z: Point3D(x, y, z)
    skeleton.extend(_get_edges(sorted(points, key=get_zyx), step,
                                       Point3D.x, Point3D.y, Point3D.z, create_point_xyz))

    create_point_zyx = lambda x, y, z: Point3D(z, y, x)
    skeleton.extend(_get_edges(sorted(points, key=get_xyz), step,
                                       Point3D.z, Point3D.y, Point3D.x, create_point_zyx))

    create_point_yxz = lambda x, y, z: Point3D(y, x, z)
    skeleton.extend(_get_edges(sorted(points, key=get_zxy), step,
                                       Point3D.y, Point3D.x, Point3D.z, create_point_yxz))

    return skeleton


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

        if _edge_eligible(points, (p,q), step, x, y, z, create_point):
            edges.append((i, i+1))

    edges = _extend_adjacent_edges([(points[a], points[b]) for a, b in edges])
    return [Segment3D(p, q) for p, q in edges]


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
