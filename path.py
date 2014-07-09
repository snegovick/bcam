import math
from state import state

class Element(object):
    def __init__(self, lt):
        self.selected = False
        self.lt = lt
        self.operations = {"drill": False}

    def draw(self, ctx):
        pass

    def distance_to_pt(self, pt):
        return 1000

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
        return 1000

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
        return math.sqrt((pt[0]-self.center[0])**2 + (pt[1]-self.center[1])**2)-self.radius

    def __repr__(self):
        return "ECircle (center: "+str(self.center)+", r: "+str(self.radius)+")\r\n"

class Path(object):
    def __init__(self, elements, name):
        self.elements = elements
        self.name = name

    def add_element(self, e):
        self.elements.append(e)

    def mk_connected_path(self):
        if len(self.elements)==0:
            return False
        ce = [] # connected elements go here
        s = self.elements[0]
        ce.append(s)
        while True:
            cont = False
            current = ce[-1]
            for e in self.elements:
                if not e.joinable:
                    continue

                if e not in ce:
                    if abs(e.start[0]-current.end[0])<0.001 and abs(e.start[1]-current.end[1])<0.001:
                        ce.append(e)
                        cont = True
                        break

            if not cont:
                print "havent found next for", current
                break

        if abs(ce[0].start[0]-ce[-1].end[0])<0.001 and abs(ce[0].start[1]-ce[-1].end[1])<0.001:
            pass # have to move joined path to separate subpath
        if len(self.elements) == len(ce):
            self.elements = ce
            return True
        return False

    def set_closed(self):
        self.closed = True

    def get_closed(self):
        return self.closed

    def draw(self, ctx, offset):
        ctx.translate(offset[0], offset[1])
        ctx.scale(state.scale[0], state.scale[1])
        for e in self.elements:
            e.draw(ctx)
        ctx.identity_matrix()
