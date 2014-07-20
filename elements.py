import math
from calc_utils import AABB, CircleUtils, LineUtils, ArcUtils, vect_len, mk_vect
from tool_operation import TOEnum

class Element(object):
    def __init__(self, lt):
        self.selected = False
        self.lt = lt
        self.operations = {TOEnum.drill: False,
                           TOEnum.exact_follow: False,
                           TOEnum.offset_follow: False}

    def draw_element(self, ctx):
        pass

    def draw(self, ctx):
        pass

    def distance_to_pt(self, pt):
        return 1000

    def get_aabb(self):
        return None

    def turnaround(self):
        return None

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

    def get_normalized_end_normal(self):
        return None

    def get_normalized_start_normal(self):
        return None

class ELine(Element):
    def __init__(self, start, end, lt):
        super(ELine, self).__init__(lt)
        self.start = start
        self.end = end
        self.joinable = True
        self.operations[TOEnum.exact_follow] = True
        self.operations[TOEnum.offset_follow] = True
        self.start_normal = None
        self.end_normal = None

    def draw_first(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])

    def draw_element(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        ctx.stroke()
    
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

    def __repr__(self):
        return "<ELine ("+str(self.start)+", "+str(self.end)+")>\r\n"

class EArc(Element):
    def __init__(self, center, radius=None, startangle=None, endangle=None, lt=None, start=None, end=None, turnaround=False):
        super(EArc, self).__init__(lt)
        self.is_turnaround = turnaround
        self.center = center

        if start != None and end != None:
            self.start = start
            self.end = end
            self.radius = vect_len(mk_vect(self.center, self.start))
            self.startangle = math.atan2(self.start[1]-self.center[1], self.start[0]-self.center[0])
            self.endangle = math.atan2(self.end[1]-self.center[1], self.end[0]-self.center[0])
        else:
            self.radius = radius
            self.startangle = math.radians(startangle)
            self.endangle = math.radians(endangle)
            self.start = (self.center[0]+math.cos(self.startangle)*self.radius, self.center[1]+math.sin(self.startangle)*self.radius)
            self.end = (self.center[0]+math.cos(self.endangle)*self.radius, self.center[1]+math.sin(self.endangle)*self.radius)

        self.joinable = True
        self.operations[TOEnum.exact_follow] = True
        self.operations[TOEnum.offset_follow] = True
        self.start_normal = None
        self.end_normal = None

    def draw_element(self, ctx):
        if self.is_turnaround:
            ctx.arc(self.center[0], self.center[1], self.radius, self.endangle, self.startangle)
        else:
            ctx.arc(self.center[0], self.center[1], self.radius, self.startangle, self.endangle)
        ctx.stroke()
    
    def draw(self, ctx):
        self.set_lt(ctx)
        self.draw_element(ctx)
        ctx.stroke()

    def draw_first(self, ctx):
        self.draw_element(ctx)

    def turnaround(self):
        return EArc(self.center, self.radius, math.degrees(self.endangle), math.degrees(self.startangle), self.lt, turnaround = not self.is_turnaround)

    def distance_to_pt(self, pt):
        au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
        return au.distance_to_pt(pt)

    def get_aabb(self):
        au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
        return au.get_aabb()

    def get_normalized_end_normal(self):
        if self.end_normal == None:
            au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
            self.end_normal = au.get_normalized_end_normal()
        return self.end_normal

    def get_normalized_start_normal(self):
        if self.start_normal == None:
            au = ArcUtils(self.center, self.radius, self.startangle, self.endangle)
            self.start_normal = au.get_normalized_start_normal()
        return self.start_normal

    def __repr__(self):
        return "<EArc ("+str(self.start)+", "+str(self.end)+")>\r\n"

class ECircle(Element):
    def __init__(self, center, radius, lt):
        super(ECircle, self).__init__(lt)
        self.center = center
        self.radius = radius
        self.start = None
        self.end = None
        self.joinable = False
        self.operations[TOEnum.drill] = True

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
