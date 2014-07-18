import math
from tool_operation import ToolOperation, TOEnum
from generalized_setting import TOSetting
from settings import settings
import cairo

class TOOffsetFollow(ToolOperation):
    def __init__(self, settings, depth=0, index=0, offset=0):
        super(TOExactFollow, self).__init__(settings)
        self.display_name = TOEnum.exact_follow+" "+str(index)
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

    def get_gcode(self):
        print self.tool.diameter
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        start = self.path.ordered_elements[0].start

        new_pos = [self.start[0], self.start[1], new_pos[2]]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth/(self.tool.diameter/2.0))+1):
            for e in self.path.ordered_elements[0]:
                if type(e).__name__ == "ELine":
                    new_pos = [e.start[0], e.start[1], -step*self.tool.diameter/2.0]
                    out+= settings.default_pp.move_to(new_pos)
                    self.tool.current_position = new_pos

                    new_pos = [e.end[0], e.end[1], -step*self.tool.diameter/2.0]
                    out+= settings.default_pp.move_to(new_pos)
                    self.tool.current_position = new_pos
                elif type(e).__name__ == "EArc":
                    if e.startangle>e.endangle:
                        new_pos = [e.start[0], e.start[1], -step*self.tool.diameter/2.0]
                        out+= settings.default_pp.move_to(new_pos)
                        self.tool.current_position = new_pos

                        new_pos = [e.end[0], e.end[1], -step*self.tool.diameter/2.0]
                        out+= settings.default_pp.mk_cw_arc(e.diameter/2.0, new_pos)
                        self.tool.current_position = new_pos
                else:
                    print "unsuported element type:", type(e).__name__

        new_pos = [new_pos[0], new_pos[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out

    def __repr__(self):
        return "<Exact follow>"
