from tool import Tool, ToolType
from generalized_setting import TOSetting
from pp_grbl import PPGRBL

class LineType:
    def __init__(self, lw=None, selected_lw=None, color=None, selected_color=None, name=None, data=None):
        if data == None:
            self.lw = lw
            self.selected_lw = selected_lw
            self.color = color
            self.selected_color = selected_color
            self.name = name
        else:
            self.deserialize(data)

    def set_lt(self, ctx):
        if len(self.color) == 3:
            ctx.set_source_rgb(self.color[0], self.color[1], self.color[2])
        else:
            ctx.set_source_rgba(self.color[0], self.color[1], self.color[2], self.color[3])
        ctx.set_line_width(self.lw)

    def set_selected_lt(self, ctx):
        if len(self.selected_color) == 3:
            ctx.set_source_rgb(self.selected_color[0], self.selected_color[1], self.selected_color[2])
        else:
            ctx.set_source_rgba(self.selected_color[0], self.selected_color[1], self.selected_color[2], self.selected_color[3])
        ctx.set_line_width(self.selected_lw)

    def serialize(self):
        return {"type": "linetype", "color": self.color, "selected_color": self.selected_color, "lw": self.lw, "selected_lw": self.selected_lw}

    def deserialize(self, data):
        self.color = data["color"]
        self.selected_color = data["selected_color"]
        self.lw = data["lw"]
        self.selected_lw = data["selected_lw"]


class Material:
    def __init__(self, data=None):
        if data == None:
            self.material_name = "default"
            self.thickness = 10
        else:
            self.deserialize(data)

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, None, self.thickness, "Thickness, mm: ", self.set_thickness_s),]
        return settings_lst

    def set_thickness_s(self, setting):
        self.thickness = setting.new_value

    def serialize(self):
        return {"type": "material", "material_name": self.material_name, "thickness": self.thickness}

    def deserialize(self, data):
        self.thickness = data["thickness"]
        self.material_name = data["material_name"]


class Settings:
    def __init__(self, data=None):
        if data == None:
            self.line_types = {"default": LineType(0.08, 0.1, (0,0,0), (1,0,0), "default")}
            self.tool = Tool("cylinder", ToolType.cylinder)
            self.material = Material()
        else:
            self.deserialize(data)


        self.select_box_lt = LineType(0.1, 0.1, (0, 1, 0, 0.2), (0, 1, 0, 0.2), "select box lt")
        self.default_pp = PPGRBL()
            

    def get_lt(self, name):
        if name in self.line_types:
            return self.line_types[name]
        return self.get_def_lt()
        
    def get_def_lt(self):
        return self.line_types["default"]

    def serialize(self):
        return {"type": "settings", "material": self.material.serialize(), "linetypes": [l.serialize() for k, l in self.line_types.iteritems()], "tool": self.tool.serialize()}

    def deserialize(self, data):
        self.material = Material(data["material"])
        self.line_types = {}
        for lt in data["line_types"]:
            self.line_types[lt["name"]] = LineType(lt)
        self.tool = Tool(data["tool"])
