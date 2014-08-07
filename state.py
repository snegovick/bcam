class State:
    def __init__(self):
        self.__total_offset = (0,0)
        self.__screen_offset = (0,0)
        self.__base_offset = (0,0)
        self.scale = (10, 10)

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

    def serialize(self):
        return {"type": "state"}

    def deserialize(self):
        pass


state = State()

