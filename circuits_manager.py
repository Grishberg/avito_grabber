#!/usr/bin/python
# -*- coding: utf-8
from range_checker import *
import response_fields as rf
from db_provider import *

ADD_TEST_RANGE = False


class CircuitsManager:
    def __init__(self, db):
        self.db = db
        self.checker = InsideChecker()

    def get_apartments_inside_circuits(self, user_id):
        print 'get ads'
        cached_ads = self.db.get_ads()
        print 'ads size:', len(cached_ads)

        ranges_set = self.db.get_circuits(user_id)
        result_set = []
        for rng in ranges_set:
            for ad in cached_ads:
                w = ad.data[rf.POS_W]
                l = ad.data[rf.POS_L]
                if w is None or l is None:
                    continue
                inside = self.checker.check(rng, Point(w, l))
                if inside:
                    result_set.append(ad)
        return result_set


def test_add_circuit(db):
    user_id = 1
    points = [Point(59.957071, 30.404679), Point(59.958965, 30.408456),
              Point(59.958986, 30.415194), Point(59.946457, 30.413909),
              Point(59.946112, 30.409081), Point(59.949106, 30.407522),
              Point(59.954670, 30.408058)]

    db.add_circuit(user_id, points)

    points = [Point(59.947807, 30.337325), Point(59.928004, 30.336278),
              Point(59.921692, 30.354259), Point(59.929622, 30.369133),
              Point(59.950377, 30.372292)]
    db.add_circuit(user_id, points)


if __name__ == '__main__':
    db = DbService()

    if ADD_TEST_RANGE:
        test_add_circuit(db)

    manager = CircuitsManager(db)
    res = manager.get_apartments_inside_circuits(1)
    print 'res', len(res)

    for r in res:
        print '    res:', r.data[rf.TITLE], r.data[rf.URL]
