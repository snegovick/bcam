from __future__ import absolute_import, division, print_function

from bcam.tool import Tool

class TOEnum(object):
    drill = "drill"
    exact_follow = "exact follow"
    offset_follow = "offset follow"
    pocket = "pocket"

class TOResult(object):
    ok = "ok"
    failed = "failed"
    repeat = "repeat"

class ToolOperation(object):
    def __init__(self, state):
        self.tool=state.settings.tool
        self.display = True
        self.selected = False

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

    def set_selected(self):
        self.selected = True

    def unset_selected(self):
        self.selected = False
