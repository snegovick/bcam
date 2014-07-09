class ToolType:
    cylinder = "cylinder"
    cone = "cone"
    ball = "ball"

class Tool(object):
    def __init__(self, name, typ, diameter=3, step=0.1, feedrate=20):
        self.diameter = diameter
        self.step = step
        self.feedrate = feedrate
        self.type = typ
        self.name = name

