from __future__ import absolute_import, division

from bcam.tool_operation import ToolOperation
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

import cairo

class TOAbstractFollow(ToolOperation):
    def __init__(self, state):
        super(TOAbstractFollow, self).__init__(state)
        self.draw_list = []

    def set_lt(self, ctx):
        if self.selected:
            self.set_selected_lt(ctx)
        else:
            ctx.set_source_rgba(1, 0, 0, 0.5)
            ctx.set_line_width(self.tool.diameter)

    def set_fill_lt(self, ctx):
        if self.selected:
            self.set_selected_fill_lt(ctx)
        else:
            ctx.set_source_rgba(0.8, 0.1, 0.1, 0.5)
            ctx.set_line_width(self.tool.diameter*0.9)

    def set_selected_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 1.0)
        ctx.set_line_width(self.tool.diameter)

    def set_selected_fill_lt(self, ctx):
        ctx.set_source_rgba(0.8, 0.1, 0.1, 1.0)
        ctx.set_line_width(self.tool.diameter*0.9)

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
        dbgfname()
        p = Singleton.state.get_path_by_name(name)
        if p == None:
            debug("  Path "+str(name)+" not found")
            return False
        return p


    def process_el_to_gcode(self, e, step):
        dbgfname()
        out = ""
        if type(e).__name__ == "ELine":
            new_pos = [e.start[0], e.start[1], -step*Singleton.state.get_tool().diameter/2.0]
            out+= Singleton.state.settings.default_pp.move_to(new_pos)
            Singleton.state.get_tool().current_position = new_pos

            new_pos = [e.end[0], e.end[1], -step*Singleton.state.get_tool().diameter/2.0]
            out+= Singleton.state.settings.default_pp.move_to(new_pos)
            Singleton.state.get_tool().current_position = new_pos
        elif type(e).__name__ == "EArc":
            if e.turnaround:
                new_pos = [e.start[0], e.start[1], -step*Singleton.state.get_tool().diameter/2.0]
                out+= Singleton.state.settings.default_pp.move_to(new_pos)
                Singleton.state.get_tool().current_position = new_pos
                new_pos = [e.end[0], e.end[1], -step*Singleton.state.get_tool().diameter/2.0]
                out+= Singleton.state.settings.default_pp.mk_ccw_arc(e.radius, new_pos)
                Singleton.state.get_tool().current_position = new_pos

            else:
                new_pos = [e.start[0], e.start[1], -step*Singleton.state.get_tool().diameter/2.0]
                out+= Singleton.state.settings.default_pp.move_to(new_pos)
                Singleton.state.get_tool().current_position = new_pos
                new_pos = [e.end[0], e.end[1], -step*Singleton.state.get_tool().diameter/2.0]
                out+= Singleton.state.settings.default_pp.mk_cw_arc(e.radius, new_pos)
                Singleton.state.get_tool().current_position = new_pos
        elif type(e).__name__ == "ECircle":
            new_pos = [e.start[0], e.start[1], -step*Singleton.state.get_tool().diameter/2.0]
            out+= Singleton.state.settings.default_pp.move_to(new_pos)
            Singleton.state.get_tool().current_position = new_pos
            new_pos = [e.end[0], e.end[1], -step*Singleton.state.get_tool().diameter/2.0]
            rel_center = [e.center[0]-e.end[0], e.center[1]-e.end[1], 0]
            out+= Singleton.state.settings.default_pp.mk_cw_ijk_arc(rel_center, new_pos)
            Singleton.state.get_tool().current_position = new_pos
            
        else:
            debug("unsuported element type: "+str(type(e).__name__))
        return out


    def get_gcode_base(self, path):
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= Singleton.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        start = path[0].start

        new_pos = [start[0], start[1], new_pos[2]]
        out+= Singleton.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth//(self.tool.diameter/2.0))+1):
            for e in path:
                out += self.process_el_to_gcode(e, step)

            new_pos = [self.tool.current_position[0], self.tool.current_position[1], self.tool.default_height]
            out+= Singleton.state.settings.default_pp.move_to_rapid(new_pos)
            self.tool.current_position = new_pos

            new_pos = [start[0], start[1], self.tool.default_height]
            out+= Singleton.state.settings.default_pp.move_to_rapid(new_pos)
            self.tool.current_position = new_pos

        new_pos = [self.tool.current_position[0], self.tool.current_position[1], self.tool.default_height]
        out+= Singleton.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out
