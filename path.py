class ELine:
    def __init__(self, start, end, lw=None):
        self.start = start
        self.end = end
        self.line_width = lw
    
    def draw(self, ctx):
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        if self.line_width != None:
            ctx.set_line_width(self.line_width)
        ctx.stroke()

    def __repr__(self):
        return "ELine ("+str(self.start)+", "+str(self.end)+")"

class Path(object):
    def __init__(self, elements, name):
        self.elements = elements
        self.closed = False
        self.name = name

    def add_element(self, e):
        self.elements.append(e)

    def set_closed(self):
        self.closed = True

    def get_closed(self):
        return self.closed

    def draw(self, ctx, offset):
        ctx.set_line_width(2)
        ctx.set_source_rgb(0.0,0.0,0.0)
        ctx.translate(offset[0], offset[1])
        for e in self.elements:
            e.draw(ctx)
        ctx.identity_matrix()
