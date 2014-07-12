import math
from tool_operation import ToolOperation, TOEnum, TOSetting, TOSettingsEnum
from state import state
from settings import settings

class TODrill(ToolOperation):
    def __init__(self, settings, center=None, depth=None):
        super(TODrill, self).__init__(settings)
        self.name = TOEnum.drill
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
        ctx.arc(self.center[0], self.center[1], (self.tool.diameter/2.0), 0, 2*math.pi);
        ctx.stroke()
        self.set_fill_lt(ctx)
        ctx.arc(self.center[0], self.center[1], (self.tool.diameter/2.0), 0, 2*math.pi);
        ctx.fill()

    def apply(self, element, depth=0):
        self.depth = depth
        if (element.operations[self.name]):
            self.center = element.center
            print self.get_gcode()
            return True
        return False

    def update(self, args):
        if "depth" in args:
            self.depth = args["depth"]
        if "center" in args:
            self.center = args["center"]

    def get_settings_list(self):
        settings_lst = [TOSetting(TOSettingsEnum.drill_depth, "float", 0, settings.material.thickness, self.depth, "Depth", self),
                       TOSetting(TOSettingsEnum.drill_center_x, "float", None, None, self.center[0], "Center x", self),
                       TOSetting(TOSettingsEnum.drill_center_y, "float", None, None, self.center[1], "Center y", self)]
        return settings_lst

    def get_gcode(self):
        print self.tool.diameter
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
