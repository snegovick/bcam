import math
from tool_operation import ToolOperation, TOEnum
from generalized_setting import TOSetting
from settings import settings
import cairo
from calc_utils import find_vect_normal, mk_vect, normalize, vect_sum, vect_len
from elements import ELine, EArc

class TOOffsetFollow(ToolOperation):
    def __init__(self, settings, depth=0, index=0, offset=0):
        super(TOOffsetFollow, self).__init__(settings)
        self.display_name = TOEnum.offset_follow+" "+str(index)
        self.name = TOEnum.offset_follow
        self.depth = depth
        self.offset = 0
        self.path = None
        self.offset_path = None

    def set_lt(self, ctx):
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.set_line_width(self.tool.diameter)

    def set_fill_lt(self, ctx):
        ctx.set_source_rgba(0.8, 0.1, 0.1, 0.5)
        ctx.set_line_width(self.tool.diameter*0.7)

    def __draw_elements(self, ctx):
        self.offset_path[0].draw_first(ctx)
        for e in self.offset_path[1:]:
            #class_name = type(e).__name__
            e.draw_element(ctx)

    def draw(self, ctx):
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); 
        self.set_lt(ctx)
        self.__draw_elements(ctx)
        ctx.stroke()
        self.set_fill_lt(ctx)
        self.__draw_elements(ctx)
        ctx.stroke()

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value
        
    def __build_offset_path(self, p):
        if len(p.elements)==0:
            return False
        if len(p.elements)==1:
            #check for circle here
            return
        
        new_elements = []
        s = p.elements[0].start
        e = p.elements[0].end
        nsn = p.elements[0].get_normalized_start_normal()
        s_pt = [nsn[0]*self.offset+s[0], nsn[1]*self.offset+s[1], 0]
        for i, e in enumerate(p.elements):
            sc = e.start # current start
            ec = e.end # current end
            

            if s_pt == None:
                nsn = e.get_normalized_start_normal()
                n = normalize(vect_sum(nsn, nen)) # sum of new start normal and prev end normal
                shift = sc
                s_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]

            if i<len(p.elements)-1:
                sn = p.elements[i+1].start # next start
                en = p.elements[i+1].end # next end

                nnsn = p.elements[i+1].get_normalized_start_normal()
                nen = e.get_normalized_end_normal()
                n = normalize(vect_sum(nnsn, nen)) # sum of next start normal and current end normal
                shift = ec
                e_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]
            else:
                nen = e.get_normalized_end_normal()
                n = nen
                shift = ec
                e_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]
            if type(e).__name__ == "ELine":
                ne = ELine(s_pt, e_pt, e.lt)
            elif type(e).__name__ == "EArc":
                ne = EArc(center=e.center, lt=e.lt, start=s_pt, end=e_pt)

            new_elements.append(ne)
            s_pt = None
            e_pt = None
        self.offset_path = new_elements
        

    def apply(self, path):
        if path.operations[self.name]:
            if path.ordered_elements!=None:
                self.path = path
                self.__build_offset_path(path)
                return True
        return False

    def get_gcode(self):
        print self.tool.diameter
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        start = self.path.ordered_elements[0].start

        new_pos = [self.start[0], self.start[1], new_pos[2]]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth/(self.tool.diameter/2.0))+1):
            for e in self.path.ordered_elements[0]:
                if type(e).__name__ == "ELine":
                    new_pos = [e.start[0], e.start[1], -step*self.tool.diameter/2.0]
                    out+= settings.default_pp.move_to(new_pos)
                    self.tool.current_position = new_pos

                    new_pos = [e.end[0], e.end[1], -step*self.tool.diameter/2.0]
                    out+= settings.default_pp.move_to(new_pos)
                    self.tool.current_position = new_pos
                elif type(e).__name__ == "EArc":
                    if e.startangle>e.endangle:
                        new_pos = [e.start[0], e.start[1], -step*self.tool.diameter/2.0]
                        out+= settings.default_pp.move_to(new_pos)
                        self.tool.current_position = new_pos

                        new_pos = [e.end[0], e.end[1], -step*self.tool.diameter/2.0]
                        out+= settings.default_pp.mk_cw_arc(e.diameter/2.0, new_pos)
                        self.tool.current_position = new_pos
                else:
                    print "unsuported element type:", type(e).__name__

        new_pos = [new_pos[0], new_pos[1], self.tool.default_height]
        out+= settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out

    def __repr__(self):
        return "<Exact follow>"
