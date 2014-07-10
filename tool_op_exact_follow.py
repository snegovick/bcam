import math
from tool_operation import ToolOperation

class TOExactFollow(ToolOperation):
    def __init__(self, settings, center=None, depth=None):
        super(TOExactFollow, self).__init__(settings)
        self.name = "drill"
        self.center = center
        self.depth = depth

    def set_lt(self, ctx):
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(3)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(2.9)

    def draw(self, ctx):
        self.set_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.tool.diameter/2.0, 0, 2*math.pi);
        ctx.stroke()
        self.set_fill_lt(ctx)
        ctx.arc(self.center[0], self.center[1], self.tool.diameter/2.0, 0, 2*math.pi);
        ctx.stroke()

    def apply(self, element):
        if (element.operations[self.name]):
            self.center = element.center
            return True
        return False

    def __repr__(self):
        return "Exact follow at "+str(self.center)
