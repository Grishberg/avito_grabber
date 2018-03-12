#!/usr/bin/python
# -*- coding: utf-8
import response_fields as rf


class Apartment:
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        return self.data[rf.URL] == other.data[rf.URL] and \
               self.data[rf.DATE] == other.data[rf.DATE]
