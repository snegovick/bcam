import math
from tool_operation import ToolOperation

class TODrill(ToolOperation):
    def __init__(self, settings, center=None, depth=None):
        super(TODrill, self).__init__(settings)
        self.name = "drill"
        self.center = center
        self.depth = depth

    def draw(self, ctx):
        ctx.arc(self.x, self.y, sekf.tool.diameter/2.0, 0, 2*math.pi);

    def apply(self, element):
        if (element.operations[self.name]):
            self.center = element.center
            return True
        return False

    def __repr__(self):
        return "Drill at "+str(self.center)
