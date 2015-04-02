from __future__ import absolute_import, division, print_function
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
    
    units = ExcUnits.metric
    points = []

    def __init__(self):
        self.regex = [{"re": ExcRE.metric, "cb": self.set_metric},
                      {"re": ExcRE.inch, "cb": self.set_inch},
                      {"re": ExcRE.point, "cb": self.add_point}]

    def set_metric(self, arg):
        self.units = ExcUnits.metric

    def set_inch(self, arg):
        self.units = ExcUnits.inches

    def add_point(self, arg):
        x = float(arg.group("x"))
        y = float(arg.group("y"))
        self.points.append((x, y))
        
    def parse_line(self, l):
        for e in self.regex:
            m = e["re"].match(l)
            if m != None:
                e["cb"](m)
                continue

    def load_from_list(self, l):
        for line in l:
            self.parse_line(line)

    def load(self, path):
        #currently only load points
        f = open(path, "r")
        state = ExcState.INIT
        for l in f:
            self.parse_line(l)

