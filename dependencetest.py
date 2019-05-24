#!/usr/bin/python

class Dependence:
    def __init__(prefix, suffix1, suffix2):
        self.prefix  = prefix
        self.suffix1 = suffix1
        self.suffix2 = suffix2

    def test(self, xform):
        return is_safe(self.suffix1, self.suffix2, xform.fst)

