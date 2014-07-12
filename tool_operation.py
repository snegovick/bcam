from tool import Tool

class TOEnum:
    drill = "drill"
    exact_follow = "exact follow"

class TOSetting:
    drill_depth = "drill_depth"
    drill_center_x = "drill_center_x"
    drill_center_y = "drill_center_y"

class ToolOperation(object):
    def __init__(self, settings_dispatcher):
        self.tool=settings_dispatcher.tool

    def draw(self, ctx):
        pass

    def apply(self, element):
        pass

    def get_gcode(self):
        return ""

    def update(self, args):
        pass

    def get_settings_dict(self):
        pass
