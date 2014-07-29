from tool_operation import ToolOperation
import cairo

class TOAbstractFollow(ToolOperation):
    def __init__(self, settings):
        super(TOAbstractFollow, self).__init__(settings)
        self.draw_list = []

    def set_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(self.tool.diameter)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(0.8, 0.1, 0.1, 1.0)
        ctx.set_line_width(self.tool.diameter*0.7)

    def __draw_elements(self, ctx):
        self.draw_list[0].draw_first(ctx)
        for e in self.draw_list[1:]:
            e.draw_element(ctx)

    def draw(self, ctx):
        if self.display:
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            self.set_lt(ctx)
            self.__draw_elements(ctx)
            ctx.stroke()
            self.set_fill_lt(ctx)
            self.__draw_elements(ctx)
            ctx.stroke()
