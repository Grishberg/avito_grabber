#!/usr/bin/python
# -*- coding: utf-8
import math


class CheckResult:
    def __init__(self, coincides):
        self.coincides = coincides
        self.hor_location = 0
        self.ver_location = 0


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.start = p1
        self.end = p2

    def check(self, p):
        x1 = self.start.x
        x2 = self.end.x
        y1 = self.start.y
        y2 = self.end.y
        hor_inside = x1 <= p.x <= x2
        ver_inside = y1 <= p.y <= y2

        dx = x1 - self.end.x
        dy = y1 - y2
        k = 1
        if dx != 0:
            k = dy / dx

        b = y2 - k * x2

        y = k * p.x + b
        coincides = (y == p.y and hor_inside) or (hor_inside and ver_inside and k == 1)
        result = CheckResult(coincides)
        if coincides:
            return result

        if k == 0:
            min_x = min(x1, x2)
            max_x = max(x1, x2)
            if p.x > max_x:
                result.hor_location = 1
            elif p.x < min_x:
                result.hor_location = -1
            return result
        x = (p.y - b) / k

        if p.x > x:
            result.hor_location = 1
        elif p.x < x:
            result.hor_location = -1
        if p.y > y:
            result.ver_location = 1
        elif p.y < y:
            result.ver_location = -1
        return result


if __name__ == '__main__':
    line = Line(Point(0, 0), Point(0, 100))
    result = line.check(Point(0, 50))
    result = line.check(Point(10, 50))
    result = line.check(Point(-10, 50))
    result = line.check(Point(-10, -50))
    result = line.check(Point(10, -50))

    line = Line(Point(0, 0), Point(100, 0))
    result = line.check(Point(50, 0))
    result = line.check(Point(-50, 0))
    result = line.check(Point(150, 0))
