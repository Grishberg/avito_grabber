#!/usr/bin/python
# -*- coding: utf-8


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
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)

        hor_inside = min_x <= p.x <= max_x
        ver_inside = min_y <= p.y <= max_y

        dx = x1 - self.end.x
        dy = y1 - y2
        k = None
        b = 0
        y = 0
        if dx != 0:
            k = dy / dx
            b = y2 - k * x2
            y = k * p.x + b
        else:
            # vertical line
            if x1 == p.x:
                return CheckResult(True)
            else:
                result = CheckResult(False)
                if ver_inside:
                    if p.x > x1:
                        result.hor_location = 1
                    elif p.x < x1:
                        result.hor_location = -1
                return result

        coincides = (y == p.y and hor_inside) or (hor_inside and ver_inside and k == None)
        result = CheckResult(coincides)
        if coincides:
            return result

        if k != 0:
            x = (p.y - b) / k
            min_x = x
            max_x = x
        if ver_inside:
            if p.x > max_x:
                result.hor_location = 1
            elif p.x < min_x:
                result.hor_location = -1
        if hor_inside:
            if p.y > y:
                result.ver_location = 1
            elif p.y < y:
                result.ver_location = -1
        return result


class InsideChecker:
    def check(self, circuit, point):
        lines = []
        prev_p = None
        for p in circuit:
            if prev_p is None:
                prev_p = p
                continue
            lines.append(Line(prev_p, p))
            prev_p = p
        lines.append(Line(prev_p, circuit[0]))

        hor = [0, 0]
        ver = [0, 0]

        for line in lines:
            result = line.check(point)
            if result.coincides:
                return True

            if result.hor_location < 0:
                hor[0] += 1
            elif result.hor_location > 0:
                hor[1] += 1
            if result.ver_location < 0:
                ver[0] += 1
            elif result.ver_location > 0:
                ver[1] += 1

        return hor[0] % 2 == 1 and hor[1] % 2 == 1 and ver[0] % 2 == 1 and ver[1] % 2 == 1


if __name__ == '__main__':
    line = Line(Point(0, 100), Point(0, 0))
    result = line.check(Point(0, 50))
    if not result.coincides:
        print "error"
    result = line.check(Point(-10, 50))
    if result.coincides or result.hor_location != -1 or result.ver_location != 0:
        print "error"

    result = line.check(Point(10, 50))
    if result.coincides or result.hor_location != 1 or result.ver_location != 0:
        print "error"

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
    result = line.check(Point(50, 50))
    result = line.check(Point(50, -50))
    result = line.check(Point(-50, -50))

    line = Line(Point(0, 0), Point(100, 100))
    result = line.check(Point(50, 50))
    if not result.coincides:
        print "error"

    result = line.check(Point(50, 55))
    if result.coincides or result.ver_location != 1 or result.hor_location != -1:
        print "error"

    checker = InsideChecker()
    points = []
    points.append(Point(0, 0))
    points.append(Point(0, 100))
    points.append(Point(100, 100))
    points.append(Point(100, 0))
    print checker.check(points, Point(10, 40))
