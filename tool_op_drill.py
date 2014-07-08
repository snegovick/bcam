import math
from tool import ToolOperation

class TODrill(ToolOperation):
    def __init__(self, x, y, depth, settings_dispatcher):
        super(TODrill, self).__init__(settings_dispatcher)
        self.x = x
        self.y = y
        self.depth = depth

    def draw(self, ctx):
        ctx.arc(self.x, self.y, sekf.tool.diameter/2.0, 0, 2*math.pi);
