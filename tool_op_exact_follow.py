import math
from tool_operation import ToolOperation, TOEnum, TOSetting
from settings import settings
import cairo

class TOExactFollow(ToolOperation):
    def __init__(self, settings, depth=0):
        super(TOExactFollow, self).__init__(settings)
        self.name = TOEnum.exact_follow
        self.depth = depth
        self.path = None

    def set_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(self.tool.diameter)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(0.8, 0.1, 0.1, 0.5)
        ctx.set_line_width(self.tool.diameter*0.7)

    def __draw_elements(self, ctx):
        self.path.ordered_elements[0].draw_first(ctx)
        for e in self.path.ordered_elements[1:]:
            #class_name = type(e).__name__
            e.draw_element(ctx)

    def draw(self, ctx):
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); 
        self.set_lt(ctx)
        self.__draw_elements(ctx)
        ctx.stroke()
        self.set_fill_lt(ctx)
        self.__draw_elements(ctx)
        ctx.stroke()

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def apply(self, path):
        if path.operations[self.name]:
            if path.ordered_elements!=None:
                print "settings path"
                self.path = path
                return True
        return False

    def __repr__(self):
        return "<Exact follow>"
