from __future__ import absolute_import, division, print_function

from bcam import loader
from bcam.calc_utils import rgb255_to_rgb1, inch_to_mm
from bcam.path import EPoint, Path
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

import re

class ExcUnits:
    metric = 0
    inches = 1

class ExcRE:
    metric = re.compile(" *METRIC, *TZ")
    inch = re.compile(" *INCH, *TZ")
    point = re.compile("X(?P<x>[\-0-9]*\.[0-9]+)Y(?P<y>[\-0-9]*\.[0-9]+)")
    def __init__(self):
        self.metric = re.compile(self.metric)
        self.inch = re.compile(self.inch)
        self.point = re.compile(self.point)
        

class ExcellonLoader(object):
    def __init__(self):
        self.units = ExcUnits.metric
        self.points = []
        self.regex = [{"re": ExcRE.metric, "cb": self.set_metric},
                      {"re": ExcRE.inch, "cb": self.set_inch},
                      {"re": ExcRE.point, "cb": self.add_point}]
        self.path = Path(Singleton.state, [], "ungrouped", Singleton.state.settings.get_def_lt().name)
        self.paths = [self.path, ]

    def set_metric(self, arg):
        self.units = ExcUnits.metric

    def set_inch(self, arg):
        self.units = ExcUnits.inches

    def add_point(self, arg):
        x = float(arg.group("x"))
        y = float(arg.group("y"))
        if (self.units == ExcUnits.inches):
            x = inch_to_mm(x)
            y = inch_to_mm(y)
        color = rgb255_to_rgb1((255, 255, 255))
        el = EPoint((x, y), Singleton.state.settings.get_def_lt(), color)
        self.path.add_element(el)
        
    def parse_line(self, l):
        for e in self.regex:
            m = e["re"].match(l)
            if m != None:
                e["cb"](m)
                continue

    def load_from_list(self, l):
        for line in l:
            self.parse_line(line)
        return self.paths

    def load(self, path):
        #currently only load points
        f = open(path, "r")
        for l in f:
            self.parse_line(l)
        return self.paths

