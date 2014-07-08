class LineType:
    def __init__(self, lw, selected_lw, color, selected_color):
        self.lw = lw
        self.selected_lw = selected_lw
        self.color = color
        self.selected_color = selected_color

class Settings:
    def __init__(self):
        self.line_types = {"default": LineType(0.2, 0.5, (0,0,0), (1,0,0))}

    def get_lt(self, name):
        return self.line_types[name]
        
    def get_def_lt(self):
        return self.line_types["default"]

settings = Settings()
