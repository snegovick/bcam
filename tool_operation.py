from tool import Tool

class TOEnum:
    drill = "drill"
    exact_follow = "exact follow"

class TOSettingsEnum:
    drill_depth = "drill_depth"
    drill_center_x = "drill_center_x"
    drill_center_y = "drill_center_y"

class TOSetting:
    def __init__(self, name, type, min, max, default, display_name, owner):
        self.name = name
        self.type = type
        self.min = min
        self.max = max
        self.default = default
        self.display_name = display_name
        self.owner = owner

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
