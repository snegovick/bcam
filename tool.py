class Tool(object):
    def __init__(self, diameter, step, feedrate):
        self.diameter = diameter
        self.step = step
        self.feedrate = feed

class ToolOperation(object):
    def __init__(self, settings_dispatcher):
        self.tool=settings_dispatcher.get_tool()

    def draw(self, ctx):
        pass
