from tool_operation import ToolOperation
from state import state

import cairo

class TOAbstractFollow(ToolOperation):
    def __init__(self, state):
        super(TOAbstractFollow, self).__init__(state)
        self.draw_list = []

    def set_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(self.tool.diameter)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(0.8, 0.1, 0.1, 1.0)
        ctx.set_line_width(self.tool.diameter*0.7)

    def __draw_elements(self, ctx):
        if self.draw_list != None:
            for e in self.draw_list:
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

    def try_load_path_by_name(self, name, state):
        p = state.get_path_by_name(name)
        if p == None:
            print "Path", name, "not found"
            return False
        return p


    def process_el_to_gcode(self, e, step):
        out = ""
        if type(e).__name__ == "ELine":
            new_pos = [e.start[0], e.start[1], -step*state.get_tool().diameter/2.0]
            out+= self.state.settings.default_pp.move_to(new_pos)
            state.get_tool().current_position = new_pos

            new_pos = [e.end[0], e.end[1], -step*state.get_tool().diameter/2.0]
            out+= self.state.settings.default_pp.move_to(new_pos)
            state.get_tool().current_position = new_pos
        elif type(e).__name__ == "EArc":
            if e.turnaround:
                new_pos = [e.start[0], e.start[1], -step*state.get_tool().diameter/2.0]
                out+= self.state.settings.default_pp.move_to(new_pos)
                state.get_tool().current_position = new_pos
                new_pos = [e.end[0], e.end[1], -step*state.get_tool().diameter/2.0]
                out+= self.state.settings.default_pp.mk_ccw_arc(e.radius, new_pos)
                state.get_tool().current_position = new_pos

            else:
                new_pos = [e.start[0], e.start[1], -step*state.get_tool().diameter/2.0]
                out+= self.state.settings.default_pp.move_to(new_pos)
                state.get_tool().current_position = new_pos
                new_pos = [e.end[0], e.end[1], -step*state.get_tool().diameter/2.0]
                out+= self.state.settings.default_pp.mk_cw_arc(e.radius, new_pos)
                state.get_tool().current_position = new_pos
        elif type(e).__name__ == "ECircle":
            new_pos = [e.start[0], e.start[1], -step*state.get_tool().diameter/2.0]
            out+= self.state.settings.default_pp.move_to(new_pos)
            state.get_tool().current_position = new_pos
            new_pos = [e.end[0], e.end[1], -step*state.get_tool().diameter/2.0]
            rel_center = [e.center[0]-e.end[0], e.center[1]-e.end[1], 0]
            out+= self.state.settings.default_pp.mk_cw_ijk_arc(rel_center, new_pos)
            state.get_tool().current_position = new_pos
            
        else:
            print "unsuported element type:", type(e).__name__
        return out
