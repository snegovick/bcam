import math
from tool_operation import ToolOperation

class TODrill(ToolOperation):
    def __init__(self, settings, center=None, depth=None):
        super(TODrill, self).__init__(settings)
        self.name = "drill"
        self.center = center
        self.depth = depth

    def set_lt(self, ctx):
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.1)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(0.0)

    def draw(self, ctx):
        self.set_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.tool.diameter/2.0, 0, 2*math.pi);
        ctx.stroke()
        self.set_fill_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.tool.diameter/2.0, 0, 2*math.pi);
        ctx.fill()

    def apply(self, element):
        if (element.operations[self.name]):
            self.center = element.center
            return True
        return False

    def __repr__(self):
        return "Drill at "+str(self.center)
