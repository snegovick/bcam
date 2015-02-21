from __future__ import absolute_import

import math
from bcam.tool_operation import ToolOperation, TOEnum
from bcam.tool_abstract_follow import TOAbstractFollow
from bcam.generalized_setting import TOSetting

import cairo
import json

class TOExactFollow(TOAbstractFollow):
    def __init__(self, state, depth=0, index=0, data=None):
        self.state = state
        super(TOAbstractFollow, self).__init__(state)
        self.name = TOEnum.exact_follow
        if data == None:
            self.depth = depth
            self.index = index
            self.path = None
        else:
            self.deserialize(data)
        self.display_name = TOEnum.exact_follow+" "+str(self.index)

    def serialize(self):
        return {'type': 'toexactfollow', 'path_ref': self.path.name, 'depth': self.depth, 'index': self.index}

    def deserialize(self, data):
        self.depth = data["depth"]
        self.index = data["index"]
        p = self.try_load_path_by_name(data["path_ref"], self.state)
        if p:
            self.apply(p)

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, self.state.settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def apply(self, path):
        if path.operations[self.name]:
            if path.ordered_elements!=None:
                self.path = path
                self.draw_list = path.ordered_elements
                return True
        return False

    def get_gcode(self):
        return self.get_gcode_base(self.path.ordered_elements)

    def __repr__(self):
        return "<Exact follow>"
