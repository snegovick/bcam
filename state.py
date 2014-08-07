from settings import Settings

class State:
    def __init__(self, data=None):
        if data == None:
            self.settings = Settings()
            self.__total_offset = (0,0)
            self.__screen_offset = (0,0)
            self.__base_offset = (0,0)
            self.scale = (10, 10)
            self.paths = []
            self.tool_operations = []
        else:
            self.deserialize(data)

    def get_offset(self):
        return self.__total_offset

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

    def serialize(self):
        return {"type": "state", "screen_offset": self.__screen_offset, "base_offset": self.__base_offset, "scale": self.scale, "settigns": self.settigns.serialize(), 'paths': [p.serialize() for p in self.paths], "tool_operations": [to.serialize() for to in self.tool_operations]}

    def get_path_by_name(self, name):
        for p in self.paths:
            if p.name == name:
                return p
        else:
            return None

    def get_tool_operation_by_name(self, name):
        for p in self.tool_operations:
            if p.name == name:
                return p
        else:
            return None

    def deserialize(self, data):
        self.__screen_offset = data["screen_offset"]
        self.__base_offset = data["base_offset"]
        self.scale = data["scale"]
        self.settings = Settings(data=data["settings"])
        self.__total_offset = (self.__base_offset[0]+self.__screen_offset[0], self.__base_offset[1]+self.__screen_offset[1])
        
        self.paths = []
        for p in data["paths"]:
            self.paths.append(Path(p))

        self.tool_operations = []
        for to in data["tool_operations"]:
            op = None
            if to["type"] == "todrill":
                op = TODrill(state=self, data=to)
            elif to["type"] == "toexactfollow":
                op = TOExactFollow(state=self, data=to)
            elif to["type"] == "tooffsetfollow":
                op = TOExactFollow(state=self, data=to)
            elif to["type"] == "topocketing":
                op = TOPocketing(state=self, data=to)
            else:
                print "Unknown tool operation:", to["type"]

            self.tool_operations.append(op)


state = State()
