from __future__ import absolute_import, division

from bcam.settings import Settings
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

class State:
    def __init__(self, data=None):
        Singleton.state = self
        self.operation_in_progress = None
        self.spinner = ['-', '\\', '|', '/']
        self.spinner_frame = 0

        if data == None:
            self.settings = Settings()
            self.__total_offset = (0,0)
            self.__screen_offset = (0,0)
            self.__base_offset = (0,0)
            self.scale = (1, 1)
            self.paths = []
            self.tool_operations = []
        else:
            self.deserialize(data)

    def set_operation_in_progress(self, operation):
        self.operation_in_progress = operation

    def get_operation_in_progress(self):
        return self.operation_in_progress

    def unset_operation_in_progress(self):
        self.operation_in_progress = None

    def get_tool(self):
        return self.settings.tool

    def is_clean(self):
        if self.paths == [] and self.tool_operations == []:
            return True
        return False

    def set(self, state):
        self.settings = state.settings
        self.__total_offset = state.__total_offset
        self.__screen_offset = state.__screen_offset
        self.__base_offset = state.__base_offset
        self.scale = state.scale
        self.paths = state.paths
        self.tool_operations = state.tool_operations

    def get_settings(self):
        return self.settings

    def get_offset(self):
        return self.__total_offset

    def get_scale(self):
        return (self.scale[0], -self.scale[1])

    def get_base_offset(self):
        return self.__base_offset

    def set_base_offset(self, offset):
        self.__base_offset = offset
        self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])

    def set_offset(self, offset):
        self.__base_offset = offset
        self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])

    def set_screen_offset(self, offset):
        if self.__screen_offset != offset:
            self.__screen_offset = offset
            self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])

    def add_paths(self, new_paths):
        self.paths+=new_paths

    def add_tool_operations(self, to):
        self.tool_operations+=to

    def serialize(self):
        return {"type": "state", "screen_offset": self.__screen_offset, "base_offset": self.__base_offset, "scale": self.scale, "settings": self.settings.serialize(), 'paths': [p.serialize() for p in self.paths], "tool_operations": [to.serialize() for to in self.tool_operations]}

    def get_path_by_name(self, name):
        for p in self.paths:
            if p.name == name:
                return p
        else:
            return None

    def get_tool_operation_by_name(self, name):
        for p in self.tool_operations:
            if p.display_name == name:
                return p
        else:
            return None

    def deserialize(self, data):
        dbgfname()
        from bcam.path import Path
        from bcam.tool_op_exact_follow import TOExactFollow
        from bcam.tool_op_offset_follow import TOOffsetFollow
        from bcam.tool_op_drill import TODrill
        from bcam.tool_op_pocketing import TOPocketing

        self.__screen_offset = data["screen_offset"]
        self.__base_offset = data["base_offset"]
        self.scale = data["scale"]
        self.settings = Settings(data=data["settings"])
        self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])
        
        self.paths = []
        for p in data["paths"]:
            self.paths.append(Path(state=self, data=p))

        self.tool_operations = []
        for to in data["tool_operations"]:
            op = None
            if to["type"] == "todrill":
                op = TODrill(state=self, data=to)
            elif to["type"] == "toexactfollow":
                op = TOExactFollow(state=self, data=to)
            elif to["type"] == "tooffsetfollow":
                op = TOOffsetFollow(state=self, data=to)
            elif to["type"] == "topocketing":
                op = TOPocketing(state=self, data=to)
            else:
                debug("  Unknown tool operation: "+str(to["type"]))
            self.tool_operations.append(op)
