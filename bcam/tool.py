from __future__ import absolute_import, division

from bcam.generalized_setting import TOSetting

class ToolType:
    cylinder = "cylinder"
    cone = "cone"
    ball = "ball"

class Tool(object):
    def __init__(self, name=None, typ=None, diameter=3, step=0.1, feedrate=20, default_height=20, data=None):
        if data == None:
            self.diameter = diameter
            self.step = step
            self.feedrate = feedrate
            self.type = typ
            self.name = name
            self.default_height = default_height
        else:
            self.deserialize(data)
        self.current_position = [0,0,0]

    def copy_tool(self, tool):
        self.diameter = tool.diameter
        self.step = tool.step
        self.feedrate = tool.feedrate
        self.type = tool.type
        self.name = tool.name
        self.default_height = tool.default_height

    def get_feedrate(self):
        return self.feedrate

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, None, self.diameter, "Diameter, mm: ", self.set_diameter_s),
                        TOSetting("float", 0, None, self.feedrate, "Feedrate, mm/min: ", self.set_feedrate_s),
                        TOSetting("float", 0, None, self.default_height, "Safe height, mm:", self.set_default_height_s)]
        return settings_lst

    def set_default_height_s(self, setting):
        self.default_height = setting.new_value

    def set_diameter_s(self, setting):
        self.diameter = setting.new_value

    def set_feedrate_s(self, setting):
        self.feedrate = setting.new_value

    def serialize(self):
        return {"type": "tool", "diameter": self.diameter, "feedrate": self.feedrate, "default_height": self.default_height, "name": self.name, "tool_type": self.type, "step": self.step}

    def deserialize(self, data):
        self.diameter = data["diameter"]
        self.feedrate = data["feedrate"]
        self.default_height = data["default_height"]
        self.name = data["name"]
        self.type = data["tool_type"]
        self.step = data["step"]
