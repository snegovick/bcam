import math

class ELine:
    def __init__(self, start, end, lw=None):
        self.start = start
        self.end = end
        self.joinable = True
        self.line_width = lw
    
    def draw(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        if self.line_width != None:
            ctx.set_line_width(self.line_width)
        ctx.stroke()

    def __repr__(self):
        return "ELine ("+str(self.start)+", "+str(self.end)+")\r\n"

class EArc:
    def __init__(self, center, radius, startangle, endangle, lw=None):
        self.center = center
        self.radius = radius
        self.startangle = math.radians(startangle)
        self.endangle = math.radians(endangle)

        self.start = (self.center[0]+math.cos(self.startangle)*self.radius, self.center[1]+math.sin(self.startangle)*self.radius)
        self.end = (self.center[0]+math.cos(self.endangle)*self.radius, self.center[1]+math.sin(self.endangle)*self.radius)

        self.joinable = True
        self.line_width = lw
    
    def draw(self, ctx):
        ctx.arc(self.center[0], self.center[1], self.radius, self.startangle, self.endangle)
        if self.line_width != None:
            ctx.set_line_width(self.line_width)
        ctx.stroke()

    def __repr__(self):
        return "EArc ("+str(self.start)+", "+str(self.end)+")\r\n"

class ECircle:
    def __init__(self, center, radius, lw=None):
        self.center = center
        self.radius = radius
        self.start = None
        self.end = None
        self.joinable = False
        self.line_width = lw
        
    def draw(self, ctx):
        ctx.arc(self.center[0], self.center[1], self.radius, 0, math.pi*2)
        if self.line_width != None:
            ctx.set_line_width(self.line_width)
        ctx.stroke()

    def __repr__(self):
        return "ECircle (center: "+str(self.center)+", r: "+str(self.radius)+")\r\n"

class Path(object):
    def __init__(self, elements, name):
        self.elements = elements
        self.closed = False
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
            self.closed = True
        if len(self.elements) == len(ce):
            self.elements = ce
            return True
        return False

    def set_closed(self):
        self.closed = True

    def get_closed(self):
        return self.closed

    def draw(self, ctx, offset, line_width, color):
        ctx.set_line_width(line_width)
        ctx.set_source_rgb(color[0], color[1], color[2])
        ctx.translate(offset[0], offset[1])
        ctx.scale(10, 10)
        for e in self.elements:
            e.draw(ctx)
        ctx.identity_matrix()
