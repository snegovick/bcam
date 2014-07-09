import math
from calc_utils import AABB, CircleUtils, LineUtils

class Element(object):
    def __init__(self, lt):
        self.selected = False
        self.lt = lt
        self.operations = {"drill": False}

    def draw(self, ctx):
        pass

    def distance_to_pt(self, pt):
        return 1000

    def get_aabb(self):
        return None

    def set_selected(self):
        self.selected = True

    def toggle_selected(self):
        self.selected = not self.selected
        return self.selected

    def set_lt(self, ctx):
        if self.lt != None:
            if self.selected:
                ctx.set_source_rgb(self.lt.selected_color[0], self.lt.selected_color[1], self.lt.selected_color[2])
                ctx.set_line_width(self.lt.selected_lw)
            else:
                ctx.set_source_rgb(self.lt.color[0], self.lt.color[1], self.lt.color[2])
                ctx.set_line_width(self.lt.lw)

class ELine(Element):
    def __init__(self, start, end, lt):
        super(ELine, self).__init__(lt)
        self.start = start
        self.end = end
        self.joinable = True
    
    def draw(self, ctx):
        self.set_lt(ctx)
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        ctx.stroke()

    def distance_to_pt(self, pt):
        lu = LineUtils(self.start, self.end)
        return lu.distance_to_pt(pt)


    def get_aabb(self):
        lu = LineUtils(self.start, self.end)
        return lu.get_aabb()

    def __repr__(self):
        return "ELine ("+str(self.start)+", "+str(self.end)+")\r\n"

class EArc(Element):
    def __init__(self, center, radius, startangle, endangle, lt):
        super(EArc, self).__init__(lt)
        self.center = center
        self.radius = radius
        self.startangle = math.radians(startangle)
        self.endangle = math.radians(endangle)

        self.start = (self.center[0]+math.cos(self.startangle)*self.radius, self.center[1]+math.sin(self.startangle)*self.radius)
        self.end = (self.center[0]+math.cos(self.endangle)*self.radius, self.center[1]+math.sin(self.endangle)*self.radius)

        self.joinable = True
    
    def draw(self, ctx):
        self.set_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.radius, self.startangle, self.endangle)
        ctx.stroke()

    def distance_to_pt(self, pt):
        return 1000

    def __repr__(self):
        return "EArc ("+str(self.start)+", "+str(self.end)+")\r\n"

class ECircle(Element):
    def __init__(self, center, radius, lt):
        super(ECircle, self).__init__(lt)
        self.center = center
        self.radius = radius
        self.start = None
        self.end = None
        self.joinable = False
        self.operations["drill"] = True
        
    def draw(self, ctx):
        self.set_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.radius, 0, math.pi*2)
        ctx.stroke()

    def distance_to_pt(self, pt):
        cu = CircleUtils(self.center, self.radius)
        return cu.distance_to_pt(pt)

    def get_aabb(self):
        cu = CircleUtils(self.center, self.radius)
        return cu.get_aabb()
        
    def __repr__(self):
        return "ECircle (center: "+str(self.center)+", r: "+str(self.radius)+")\r\n"
