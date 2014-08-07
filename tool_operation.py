from tool import Tool

class TOEnum:
    drill = "drill"
    exact_follow = "exact follow"
    offset_follow = "offset follow"
    pocket = "pocket"

class ToolOperation(object):
    def __init__(self, settings_dispatcher):
        self.tool=settings_dispatcher.tool
        self.display = True

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

    def serialize(self):
        return "Unimplemented serialization for abstract tool operation"

    def deserialize(self, data):
        pass
