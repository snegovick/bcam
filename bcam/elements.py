from __future__ import absolute_import

import math
from bcam.calc_utils import (AABB, CircleUtils, LineUtils, ArcUtils, PointUtils,
                             vect_len, mk_vect)
from bcam.tool_operation import TOEnum

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname


import json

class Element(object):
    def __init__(self, lt):
        self.selected = False
        self.lt = lt
        self.operations = {TOEnum.drill: False,
                           TOEnum.exact_follow: False,
                           TOEnum.offset_follow: False}

    def draw_element(self, ctx):
        pass

    def draw_first(self, ctx):
        pass

    def draw(self, ctx):
        pass

    def distance_to_pt(self, pt):
        return 1000

    def get_aabb(self):
        return None

    def turnaround(self):
        return None

    def serialize(self):
        return 'Unimplemented serialization for abstract element'

    def deserialize(self, data):
        pass

    def set_color(self, ctx):
        ctx.set_source_rgb(self.color[0], self.color[1], self.color[2])

    def set_selected(self):
        self.selected = True

    def unset_selected(self):
        self.selected = False

    def toggle_selected(self):
        self.selected = not self.selected
        return self.selected

    def set_lt(self, ctx):
        if self.lt != None:
            if self.selected:
                self.lt.set_selected_lt(ctx)
            else:
                self.lt.set_lt(ctx)
                self.set_color(ctx)
                

    def get_normalized_end_normal(self):
        return None

    def get_normalized_start_normal(self):
        return None

class ELine(Element):
    def __init__(self, start=None, end=None, lt=None, color=None, data=None):
        super(ELine, self).__init__(lt)
        if data == None:
            self.start = start
            self.end = end
            self.color = color
        else:
            self.deserialize(data)
        self.joinable = True
        self.operations[TOEnum.exact_follow] = True
        self.operations[TOEnum.offset_follow] = True
        self.start_normal = None
        self.end_normal = None

    def serialize(self):
        return {'type': 'eline', 'start': self.start, 'end': self.end, 'color': self.color}
        
    def deserialize(self, data):
        self.start = data["start"]
        self.end = data["end"]
        self.color = data["color"]

    def draw_first(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])

    def draw_element(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
    
    def draw(self, ctx):
        self.set_lt(ctx)
        self.draw_first(ctx)
        ctx.stroke()

    def distance_to_pt(self, pt):
        lu = LineUtils(self.start, self.end)
        return lu.distance_to_pt(pt)

    def turnaround(self):
        return ELine(self.end, self.start, self.lt)

    def get_aabb(self):
        lu = LineUtils(self.start, self.end)
        return lu.get_aabb()

    def get_normalized_end_normal(self):
        if self.end_normal == None:
            lu = LineUtils(self.start, self.end)
            self.end_normal = lu.get_normalized_end_normal()
        return self.end_normal

    def get_normalized_start_normal(self):
        if self.start_normal == None:
            lu = LineUtils(self.start, self.end)
            self.start_normal = lu.get_normalized_start_normal()
        return self.start_normal

    def get_cu(self):
        return LineUtils(self.start, self.end)

    def __repr__(self):
        return "<ELine ("+str(self.start)+", "+str(self.end)+")>\r\n"

class EArc(Element):
    def __init__(self, center=None, radius=None, startangle=None, endangle=None, lt=None, start=None, end=None, turnaround=False, color=None, data=None):
        super(EArc, self).__init__(lt)
        if data == None:
            self.is_turnaround = turnaround
            self.color = color
            if start != None and end != None:
                self.init_from_pt(start, end, center)
            else:
                self.init_from_angles(radius, startangle, endangle, center)
        else:
            self.deserialize(data)

        self.joinable = True
        self.operations[TOEnum.drill] = True
        self.operations[TOEnum.exact_follow] = True
        self.operations[TOEnum.offset_follow] = True
        self.start_normal = None
        self.end_normal = None

    def to_line_sequence(self, precision):
        dbgfname()
        sa = self.startangle
        ea = self.endangle
        if sa > ea:
            ea+=math.pi*2
        da = (ea - sa)

        n_steps = int(da/precision)
        s_pt = (self.center[0]+math.cos(sa)*self.radius, self.center[1]+math.sin(sa)*self.radius)
        debug("  splitting arc, start angle: "+str(sa)+" start_pt: "+str(s_pt))

        converted_elements = []

        for i in range(1,n_steps):
            a = sa+i*0.1
            e_pt = (self.center[0]+math.cos(a)*self.radius, self.center[1]+math.sin(a)*self.radius)
            ne = ELine(s_pt, e_pt, self.lt, self.color)
            debug("  angle: "+str(a)+" line: "+str(s_pt)+" "+str(e_pt))
            s_pt = e_pt
            converted_elements.append(ne)
        e_pt = self.end
        ne = ELine(s_pt, e_pt, self.lt, self.color)
        converted_elements.append(ne)
        return converted_elements

    def init_from_pt(self, start, end, center):
        self.center = center
        self.start = start
        self.end = end
        self.radius = vect_len(mk_vect(self.center, self.start))
        self.startangle = math.atan2(self.start[1]-self.center[1], self.start[0]-self.center[0])
        self.endangle = math.atan2(self.end[1]-self.center[1], self.end[0]-self.center[0])

    def init_from_angles(self, radius, startangle, endangle, center):
        self.center = center
        self.radius = radius
        self.startangle = math.radians(startangle)
        self.endangle = math.radians(endangle)
        self.start = (self.center[0]+math.cos(self.startangle)*self.radius, self.center[1]+math.sin(self.startangle)*self.radius)
        self.end = (self.center[0]+math.cos(self.endangle)*self.radius, self.center[1]+math.sin(self.endangle)*self.radius)

    def serialize(self):
        return {'type': 'earc', 'radius': self.radius, 'center': self.center, 'startangle': self.startangle, 'endangle': self.endangle, 'turnaround': self.is_turnaround, 'color': self.color}

    def deserialize(self, data):
        self.init_from_angles(data["radius"], math.degrees(data["startangle"]), math.degrees(data["endangle"]), data["center"])
        self.center = data["center"]
        self.is_turnaround = data["turnaround"]
        self.color = data["color"]

    def draw_element(self, ctx):
        if self.is_turnaround:
            ctx.arc(self.center[0], self.center[1], self.radius, self.endangle, self.startangle)
        else:
            ctx.arc(self.center[0], self.center[1], self.radius, self.startangle, self.endangle)
    
    def draw(self, ctx):
        self.set_lt(ctx)
        self.draw_element(ctx)
        ctx.stroke()

    def draw_first(self, ctx):
        self.draw_element(ctx)

    def turnaround(self):
        debug("In EArc.turnaround")
        debug("  arc turnaround, start: "+str(self.start)+" end: "+str(self.end))
        arc = EArc(self.center, self.radius, start = self.end, end = self.start, lt = self.lt, turnaround = not self.is_turnaround)
        debug("  new arc, start: "+str(arc.start)+" end: "+str(arc.end))
        return arc

    def distance_to_pt(self, pt):
        au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
        return au.distance_to_pt(pt)

    def get_aabb(self):
        au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
        return au.get_aabb()

    def get_normalized_end_normal(self):
        if self.end_normal == None:
            au = None
            au = ArcUtils(self.center, self.radius, self.startangle, self.endangle, self.is_turnaround)
            self.end_normal = au.get_normalized_end_normal()
        return self.end_normal

    def get_normalized_start_normal(self):
        if self.start_normal == None:
            au = ArcUtils(self.center, self.radius, self.startangle, self.endangle, self.is_turnaround)
            self.start_normal = au.get_normalized_start_normal()
        return self.start_normal

    def get_cu(self):
        return ArcUtils(self.center, self.radius, self.startangle, self.endangle)


    def __repr__(self):
        return "<EArc ("+str(self.start)+", "+str(self.end)+", ta: "+str(self.is_turnaround)+")>\r\n"

class ECircle(Element):
    def __init__(self, center=None, radius=None, lt=None, color=None, data=None):
        if data == None:
            self.center = center
            self.radius = radius
            self.color = color
        else:
            self.deserialize(data)

        super(ECircle, self).__init__(lt)
        self.joinable = False
        self.operations[TOEnum.drill] = True
        self.start = [self.center[0]+self.radius, self.center[1]]
        self.end = [self.center[0]+self.radius, self.center[1]]


    def serialize(self):
        return {'type': 'ecircle', 'radius': self.radius, 'center': self.center, 'color': self.color}

    def deserialize(self, data):
        self.radius = data["radius"]
        self.center = data["center"]
        self.color = data["color"]

    def draw_element(self, ctx):
        ctx.arc(self.center[0], self.center[1], self.radius, 0, math.pi*2)

    def draw_first(self, ctx):
        self.draw_element(ctx)
        
    def draw(self, ctx):
        self.set_lt(ctx)
        self.draw_element(ctx)
        ctx.stroke()

    def distance_to_pt(self, pt):
        cu = CircleUtils(self.center, self.radius)
        return cu.distance_to_pt(pt)

    def get_aabb(self):
        cu = CircleUtils(self.center, self.radius)
        return cu.get_aabb()
        
    def __repr__(self):
        return "<ECircle (center: "+str(self.center)+", r: "+str(self.radius)+")>\r\n"

class EPoint(Element):
    def __init__(self, center=None, lt=None, color=None, data=None):
        if data == None:
            self.center = center
            self.color = color
        else:
            self.deserialize(data)

        super(EPoint, self).__init__(lt)
        self.joinable = False
        self.operations[TOEnum.drill] = True

    def serialize(self):
        return {'type': 'epoint', 'center': self.center, 'color': self.color}

    def deserialize(self, data):
        self.center = data["center"]
        self.color = data["color"]

    def draw_element(self, ctx):
        ctx.rectangle(self.center[0]-0.1, self.center[1]-0.1, 0.2, 0.2)

    def draw_first(self, ctx):
        self.draw_element(ctx)
        
    def draw(self, ctx):
        self.set_lt(ctx)
        self.draw_element(ctx)
        ctx.stroke()

    def distance_to_pt(self, pt):
        pu = PointUtils(self.center)
        return pu.distance_to_pt(pt)

    def get_aabb(self):
        pu = PointUtils(self.center)
        return pu.get_aabb()
        
    def __repr__(self):
        return "<EPoint (center: "+str(self.center)+")>\r\n"
