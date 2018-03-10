#!/usr/bin/python
# -*- coding: utf-8
from Apartment import *


# returns new ads if exists.
def find_new_ads(x, y):
    return [item for item in x if item not in y]


if __name__ == '__main__':

    new_ads = [Apartment({"url": "url1", "data": 1}), Apartment({"url": "url2", "data": 2})]
    old_ads = [Apartment({"url": "url3", "data": 1}), Apartment({"url": "url4", "data": 2}),
               Apartment({"url": "url2", "data": 3})]
    res = find_new_ads(new_ads, old_ads)
    for r in res:
        print r.data
