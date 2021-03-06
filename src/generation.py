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


def generate_interval2D(p_min, p_max, step, allow_kissing):
    xMin = p_min.x()
    yMin = p_min.y()
    xMax = p_max.x()
    yMax = p_max.y()

    if xMin >= xMax or yMin >= yMax:
        return []

    rects = [] # tuples of points (bottom_left, top_right)

    # for initialization for first bottom_left that MUST be p_min
    old_bottom_left = Point2D(yMin, yMin)
    old_top_right = Point2D(xMin, yMin+(step if not allow_kissing else 0))

    # generate the rectangles
    while old_top_right.x() < xMax and old_top_right.y() < yMax:
        bottom_left = Point2D(old_top_right.x(),
                              randrange(old_bottom_left.y(),
                                        old_top_right.y()+(step if allow_kissing else 0),
                                        step))
        top_right = Point2D(randrange(bottom_left.x()+step,
                                      xMax+step,
                                      step),
                            randrange(old_top_right.y()+ \
                                                (step if bottom_left.y() == old_bottom_left.y() or
                                                         bottom_left.y() == old_top_right.y() else 0),
                                      yMax+step,
                                      step))
        rects.append((bottom_left, top_right))
        old_bottom_left = bottom_left
        old_top_right   = top_right

    # force the last top right to be p_max
    rects[-1] = (rects[-1][0], p_max)

    # get lower and upper line from the rectangles
    lower_line = [rects[0][0]]
    upper_line = [Point2D(rects[0][0].x(), rects[0][1].y())]
    for s in rects:
        if s[0].y() != lower_line[-1].y():
            lower_line.append(Point2D(s[0].x(), lower_line[-1].y()))
            lower_line.append(s[0])
        if s[1].y() != upper_line[-1].y():
            upper_line.append(Point2D(s[0].x(), upper_line[-1].y()))
            upper_line.append(Point2D(s[0].x(), s[1].y()))
    lower_line.append(Point2D(rects[-1][1].x(), rects[-1][0].y()))
    upper_line.append(rects[-1][1])

    upper_line.reverse()
    lower_line.extend(upper_line)
    return interval.Interval2D(lower_line, rects)


def generate_interval2D_broken(p_min, p_max, step, allow_kissing):
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
    for i in xrange(xMin+step, xMax, step):
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
                if square_up and old_high == old_low:
                    # lower_line has expanded, upper_line want to,
                    # raise the new upper_line threshold
                    # so that upper and lower lines don't "kiss"
                    old_high += step
                    high += step
                    upper_line[-1].get()[1] += step
                if old_high < yMax: # don't add points above yMax
                    # add points to make the upper_line rectilinear
                    upper_line.append(Point2D(i, old_high))
                    square_up = Point2D(i, old_high)
                    old_high = high if high <= yMax else yMax
                    upper_line.append(Point2D(i, old_high))
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


def generate_interval3D(p_min, p_max, step, allow_degenerate):
    # generate three random 2D intervals
    xy = generate_interval2D(p_min, p_max, step, allow_degenerate)
    xz = generate_interval2D(p_min, p_max, step, allow_degenerate)
    yz = generate_interval2D(p_min, p_max, step, allow_degenerate)

    # get the 3D points
    points = _points3d_from_intervals2D(p_min, p_max, xy, xz, yz, step)

    if not allow_degenerate:
        points = _clean_flat_faces(points, step)

    # extract the skeleton from the points
    skeleton = []

    get_yzx = lambda p: (p.y(), p.z(), p.x())
    get_xyz = lambda p: (p.x(), p.y(), p.z())
    get_zxy = lambda p: (p.z(), p.x(), p.y())

    # create_points for 3D edges
    create_point_xzy = lambda x, y, z: Point3D(x, z, y)
    create_point_zyx = lambda x, y, z: Point3D(z, y, x)
    create_point_yxz = lambda x, y, z: Point3D(y, x, z)
    # create_points for new interval2Ds
    create_point_xyz = lambda x, y, z: Point3D(x, y, z)
    create_point_yzx = lambda x, y, z: Point3D(y, z, x)
    create_point_zxy = lambda x, y, z: Point3D(z, x, y)

    x, y, z = Point3D.x, Point3D.y, Point3D.z

    edges_xz = _get_edges(sorted(points, key=get_yzx), step, x, z, y, create_point_xzy)
    edges_zy = _get_edges(sorted(points, key=get_xyz), step, z, y, x, create_point_zyx)
    edges_yx = _get_edges(sorted(points, key=get_zxy), step, y, x, z, create_point_yxz)

    skeleton.extend(edges_xz)
    skeleton.extend(edges_zy)
    skeleton.extend(edges_yx)

    # new projections
    interval_xy = _get_interval2D(edges_xz, x, y, create_point_xyz)
    interval_zx = _get_interval2D(edges_zy, z, x, create_point_yzx)
    interval_yz = _get_interval2D(edges_yx, y, z, create_point_zxy)

    if interval_xy is None or \
       interval_zx is None or \
       interval_yz is None:
        print "Structure not connected, try again."
        return interval.Interval3D()

    return interval.Interval3D(skeleton, interval_xy, interval_zx, interval_yz)


def _points3d_from_intervals2D(p_min, p_max, xy, xz, yz, step):
    points = []
    for x in xrange(int(p_min.x()), int(p_max.x()) + step, step):
        for y in xrange(int(p_min.y()), int(p_max.y()) + step, step):
            for z in xrange(int(p_min.z()), int(p_max.z()) + step, step):
                if Point2D(x, y) in xy and \
                   Point2D(x, z) in xz and \
                   Point2D(y, z) in yz:
                    points.append(Point3D(x, y, z))

    return points


def _clean_flat_faces(points, step):
    length = 0
    right = left = up = down = front = back = dict()
    while length != len(points):
        length = len(points)
        for p in points:
            has_right  = right.get(p, Point3D(p.x()+step, p.y(),      p.z()     ) in points)
            has_left   = left .get(p, Point3D(p.x()-step, p.y(),      p.z()     ) in points)
            has_up     = up   .get(p, Point3D(p.x(),      p.y()+step, p.z()     ) in points)
            has_down   = down .get(p, Point3D(p.x(),      p.y()-step, p.z()     ) in points)
            has_front  = front.get(p, Point3D(p.x(),      p.y(),      p.z()+step) in points)
            has_back   = back .get(p, Point3D(p.x(),      p.y(),      p.z()-step) in points)
            if (not has_up    and not has_down ) or \
               (not has_front and not has_back ) or \
               (not has_left  and not has_right):
               points.remove(p)

    return points


def _get_interval2D(edges, x, y, create_point):
    # extend adjacent edges and project them on xy
    ext_2d_edges = []

    # edges are horizontal (e.a.y = e.b.y and e.a.x < e.b.x)
    y_ref = y(edges[0].a)
    min_x = x(edges[0].a)
    max_x = x(edges[0].b)
    for e in edges:
        if y(e.a) != y_ref:
            ext_2d_edges.append(
                Edge3D(create_point(min_x, y_ref, 0), create_point(max_x, y_ref, 0)))
            min_x, max_x = x(e.a), x(e.b)
            y_ref = y(e.a)
        elif x(e.b) > max_x:
            max_x = x(e.b)

    ext_2d_edges.append(
        Edge3D(create_point(min_x, y_ref, 0), create_point(max_x, y_ref, 0)))

    # now, retrieve interval2D points (don't care about squares atm)
    int_points = []

    lower_line = []
    # get lower line's points
    lower_line.append(ext_2d_edges[0].a)
    lower_line.append(ext_2d_edges[0].b)
    for e in ext_2d_edges[1:]:
        if x(e.b) > x(lower_line[-1]):
            if x(e.a) > x(lower_line[-1]): # structure not connected
                return None
            lower_line.append(create_point(x(lower_line[-1]), y(e.b), 0))
            lower_line.append(e.b)

    upper_line = []
    # get upper line's points
    upper_line.append(ext_2d_edges[-1].b)
    upper_line.append(ext_2d_edges[-1].a)
    for e in ext_2d_edges[::-1]:
        if x(e.a) < x(upper_line[-1]):
            # no need to test if edges are connected here
            # because we would have detect it above
            upper_line.append(create_point(x(upper_line[-1]), y(e.a), 0))
            upper_line.append(e.a)

    int_points = lower_line[:]
    int_points.extend(upper_line)

    # ok, now let's extract the squares from lower and upper line
    squares = []
    candidates = [] # tuples of vertical bottom_left, top_right (asynchronous)

    # to treat candidates when the upper_line has some thresholds
    # after the last threshold of lower_line, we upper_line[0] (Point(xmax, ymax))
    lower_line.append(upper_line[0])
    upper_line.reverse() # make it go up

    i = 0 # index in lower_line
    j = 1 # index in upper_line
    # we iterate through lower and upper_line simultaneously,
    # and mark all bottom_left and top_right points, but verticaly
    while i < len(lower_line) and j < len(upper_line):
        low = lower_line[i]
        up  = upper_line[j]
        if x(low) < x(up):
            candidates.append((low, create_point(x(low), y(up), 0)))
            old_low_y = y(low)
            i += 2
        elif x(low) > x(up):
            candidates.append((create_point(x(up), old_low_y, 0), up))
            j += 2
        else: # x(low) == x(up)
            candidates.append((low, up))
            old_low_y = y(low)
            i += 2
            j += 2

    # squares are formed by the bottom left of a candidate
    # and the top left of the next candidate
    for i in xrange(len(candidates)-1):
        squares.append((candidates[i][0], candidates[i+1][1]))

    return interval.Interval2D(int_points, squares)


def _get_edges(points, step, x, y, z, create_point):
    edges = [] # unitary edges

    y_ref = y(points[0])
    z_ref = z(points[0])
    for i in xrange(len(points)-1):
        p = points[i  ]
        q = points[i+1]

        if y(q) != y_ref or z(q) != z_ref:
            y_ref = y(q)
            z_ref = z(q)
            continue

        edge_type = _compute_edge_type(points, (p,q), step, x, y, z, create_point)
        if edge_type != Edge3D.UNKNOWN:
            edges.append(Edge3D(p, q, edge_type))

    #edges = _extend_adjacent_edges([(points[a], points[b], t) for a, b, t in edges])
    return _extend_adjacent_edges(edges)#[Edge3D(p, q, t) for p, q, t in edges]


def _compute_edge_type(points, e, step, x, y, z, create_point, first=True):
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
            if   p_back  and q_back  and not p_up_back    and not q_up_back:
                return Edge3D.CONCAVE1
            elif p_front and q_front and not p_down_front and not q_down_front:
                return Edge3D.CONCAVE2
            else:
                return Edge3D.UNKNOWN

        elif (p_front and p_back) and (q_front and q_back):
            if   p_up   and q_up   and not p_up_back    and not q_up_back:
                return Edge3D.CONCAVE1
            elif p_down and q_down and not p_down_front and not q_down_front:
                return Edge3D.CONCAVE2
            else:
                return Edge3D.UNKNOWN

    # lonely edge that connect two cubical complexes
    #b = (p_up and p_front and not p_down and not p_back and \
         #q_back and q_down and not q_up and q_down) or \
        #(q_up and q_front and not q_down and not q_back and \
         #p_back and p_down and not p_up and p_down)

    # convex
    return Edge3D.CONVEX


def _extend_adjacent_edges(edges):
    merged_edges = []
    first = ()
    streak = False
    for i in xrange(len(edges)-1):
        e1 = edges[i  ]
        e2 = edges[i+1]
        if e1.b == e2.a and e1.type == e2.type:
            if not streak:
                first = e1
                streak = True
        else:
            merged_edges.append(Edge3D(first.a, e1.b, first.type) if streak else e1)
            streak = False

    merged_edges.append(Edge3D(first.a, edges[-1].b, first.type) if streak else edges[-1])
    return merged_edges

