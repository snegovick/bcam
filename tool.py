from generalized_setting import TOSetting

class ToolType:
    cylinder = "cylinder"
    cone = "cone"
    ball = "ball"

class Tool(object):
    def __init__(self, name, typ, diameter=3, step=0.1, feedrate=20, default_height=20):
        self.diameter = diameter
        self.step = step
        self.feedrate = feedrate
        self.type = typ
        self.name = name
        self.default_height = default_height
        self.current_position = [0,0,0]

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, None, self.diameter, "Diameter, mm: ", self.set_diameter_s),
                        TOSetting("float", 0, None, self.feedrate, "Feedrate, mm/min: ", self.set_feedrate_s)]
        return settings_lst

    def set_diameter_s(self, setting):
        self.diameter = setting.new_value

    def set_feedrate_s(self, setting):
        self.feedrate = setting.new_value
