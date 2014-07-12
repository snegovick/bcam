from tool import Tool

class TOEnum:
    drill = "drill"
    exact_follow = "exact follow"

class TOSetting:
    def __init__(self, type, min, max, default, display_name, parent_cb):
        self.type = type
        self.min = min
        self.max = max
        self.default = default
        self.display_name = display_name
        self.new_value = None
        self.parent_callback = parent_cb

    def set_value(self, v):
        self.new_value = v
        self.parent_callback(self)

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

    def get_settings_list(self):
        return []
