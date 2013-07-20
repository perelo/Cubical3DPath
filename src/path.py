#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__author__ = 'Eloi Perdereau'
__date__ = '20-07-2013'


from interval import *


def visible(interval, p, q):
    if not isinstance(interval, Interval2D):
        return False

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
        if not s.intersect(Segment(s1[1], s2[0])):
            return False

    return True

