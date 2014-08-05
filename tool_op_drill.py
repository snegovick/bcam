import math
from tool_operation import ToolOperation, TOEnum
from generalized_setting import TOSetting
from state import state
from settings import settings

import json

class TODrill(ToolOperation):
    def __init__(self, settings, center=None, depth=0, index=0):
        super(TODrill, self).__init__(settings)
        self.display_name = TOEnum.drill+" "+str(index)
        self.name = TOEnum.drill
        if center!=None:
            self.center = list(center)
        else:
            self.center = None
        self.depth = depth

    def serialize(self):
        return json.dumps({'type': 'todrill', 'center': self.center, 'depth': self.depth, 'index': self.index})

    def deserialize(self, data):
        pass

    def set_lt(self, ctx):
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.1)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(0.0)

    def draw(self, ctx):
        if self.display:
            self.set_lt(ctx)
            ctx.arc(self.center[0], self.center[1], (self.tool.diameter/2.0), 0, 2*math.pi);
            ctx.stroke()
            self.set_fill_lt(ctx)
            ctx.arc(self.center[0], self.center[1], (self.tool.diameter/2.0), 0, 2*math.pi);
            ctx.fill()

    def apply(self, element, depth=0):
        self.depth = depth
        if (element.operations[self.name]):
            self.center = list(element.center)
            return True
        return False

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),
                        TOSetting("float", None, None, self.center[0], "Center x, mm: ", self.set_center_x_s),
                        TOSetting("float", None, None, self.center[1], "Center y, mm: ", self.set_center_y_s)]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def set_center_x_s(self, setting):
        self.center[0] = setting.new_value

    def set_center_y_s(self, setting):
        self.center[1] = setting.new_value

    def get_gcode(self):
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        new_pos = [self.center[0], self.center[1], new_pos[2]]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth/(self.tool.diameter/2.0))+1):
            new_pos = [self.center[0], self.center[1], -step*self.tool.diameter/2.0]
            out+= settings.default_pp.move_to(new_pos)
            self.tool.current_position = new_pos

        new_pos = [self.center[0], self.center[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out

    def __repr__(self):
        return "<Drill at "+str(self.center)+">"
