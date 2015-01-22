import math
from tool_operation import ToolOperation, TOEnum
from tool_abstract_follow import TOAbstractFollow
from generalized_setting import TOSetting
from calc_utils import find_vect_normal, mk_vect, normalize, vect_sum, vect_len, linearized_path_aabb, LineUtils
from elements import ELine, EArc, EPoint

from logging import debug, info, warning, error, critical
from util import dbgfname

import json
import cairo


class TOPocketing(TOAbstractFollow):
    def __init__(self, state, depth=0, index=0, offset=0, data=None):
        super(TOAbstractFollow, self).__init__(state)
        self.state = state
        self.name = TOEnum.pocket
        if data == None:
            self.index = index
            self.depth = depth
            self.offset = 0
            self.path = None
            self.offset_path = None
        else:
            self.deserialize(data)
        self.display_name = TOEnum.pocket+" "+str(self.index)

    def serialize(self):
        return {'type': 'topocketing', 'path_ref': self.path.name, 'depth': self.depth, 'index': self.index, 'offset': self.offset}

    def __linearize_path(self, path, tolerance):
        linearized_path = []
        for e in path:
            if type(e).__name__ == "EArc":
                lpath = e.to_line_sequence(tolerance)
                linearized_path += lpath
            elif type(e).__name__ == "ELine":
                linearized_path.append(e)
        return linearized_path

    def __is_element_crossing(self, el_coords):
        return abs(el_coords[0][1])/el_coords[0][1] != abs(el_coords[1])/el_coords[1]

    def __is_crossing_up(self, el_coords):
        if el_coords[1][1] > el_coords[0][1]:
            return True
        return False

    def __is_point_at_left(self, pt, element, up):
        
        v1x = element.start[0]-pt[0]
        v1y = element.start[1]-pt[1]

        v2x = element.end[0]-element.start[0]
        v2y = element.end[1]-element.start[1]

        cross_product = v1x*v2y-v1y*v2x
        if (up and (cross_product > 0)):
            return True
        elif (not up) and (cross_product < 0):
            return True
        return False

    def __is_pt_inside_path_winding(self, pt, path):
        dbgfname()
        e = path[0]

        turns = 0
        
        for e in path:
            sx = e.start[0] - pt[0]
            sy = e.start[1] - pt[1]
            ex = e.end[0] - pt[0]
            ey = e.end[1] - pt[1]
            
            
        debug("  cur ang: "+str(abs_angle))
        abs_angle = abs(abs_angle)
        if (abs_angle>=math.pi*2):
            turns+=1
        #while (abs_angle>=math.pi*2):
        #    abs_angle -= math.pi*2
        #    turns+=1
        if (abs(turns) >= 1):
            return True
        return False

    def __is_pt_inside_path_intersections(self, pt, path, aabb):
        #dbgfname()
        #debug("  pt:"+str(pt))
        #debug("  path:"+str(path))
        left = aabb.left - 10
        right = aabb.right + 10
        top = aabb.top + 10
        bottom = aabb.bottom - 10
        start = [left, pt[1]]
        end = [right, pt[1]]
        pt_line0 = LineUtils(start, end)

        start = [left, bottom]
        end = [right, top]
        pt_line45 = LineUtils(start, end)

        start = [left, top]
        end = [right, bottom]
        pt_line135 = LineUtils(start, end)

        #lines = [pt_line0, pt_line45, pt_line135]
        lines = [pt_line0]

        intersections = []

        for l in lines:
            line_intersections = []
            for e in path:
                util = e.get_cu()
                intersection = util.find_intersection(l)
                if (intersection != None):
                    line_intersections.append(intersection)
            if len(line_intersections) != 0:
                intersections.append(line_intersections)

                
        if len(intersections) == 0:
            return False
        intersections = min(intersections, key=lambda l: len(l))

        n_intersections_on_left = 0
        #debug("  intersections:"+str(intersections))
        for i in intersections:
            if (i[0] < pt[0]):
                n_intersections_on_left += 1
                
        #debug("  n_intersections_on_left:"+str(n_intersections_on_left))
        if (n_intersections_on_left % 2) != 0:
            return True
        return False

    def build_points(self, path):
        dbgfname()
        debug("  linearizing path")
        #lpath = self.__linearize_path(path, 0.1)
        lpath = path

        path_aabb = linearized_path_aabb(lpath)
        left = path_aabb.left - 10
        right = path_aabb.right + 10
        top = path_aabb.top + 10
        bottom = path_aabb.bottom - 10
        points = []
        step = 0.1
        total_points = int(right-left+1)*int(top-bottom+1)/step
        debug("  AABB: "+str(path_aabb))
        point_counter = 0
        x = left
        while (x<right):
            y = bottom
            while (y<top):
                debug("  checking pt: "+str(x)+" "+str(y)+" "+str(point_counter)+"/"+str(total_points))
                if self.__is_pt_inside_path_winding((x, y), lpath):
                    points.append(EPoint(center=[x, y], lt=self.state.settings.get_def_lt()))
                    debug("  it fits")
                point_counter += 1
                y += step
            x += step
        debug("  points: "+str(points))
        return points
            
    def deserialize(self, data):
        self.depth = data["depth"]
        self.index = data["index"]
        self.offset = data["offset"]
        p = self.try_load_path_by_name(data["path_ref"], self.state)
        if p:
            self.apply(p)

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, self.state.settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),
                        TOSetting("float", None, None, 0, "Offset, mm: ", self.set_offset_s)]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def set_offset_s(self, setting):
        self.offset = setting.new_value
        #self.__build_offset_path(self.path)
        #self.__build_pocket_path()
        #self.draw_list = self.offset_path+self.pocket_pattern
        
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

    def __build_pocket_path(self):
        dbgfname()
        # find bounding box
        points_x = []
        points_y = []
        for e in self.offset_path:
            points_x.append(e.start[0])
            points_x.append(e.end[0])
            points_y.append(e.start[1])
            points_y.append(e.end[1])

        left = min(points_x) - 10.0
        right = max(points_x) + 10.0
        top = max(points_y) + 10.0
        bottom = min(points_y) - 10.0

        
        #generate linear fill pattern
        linear_pattern = []
        dy = top - bottom
        dx = right - left
        debug("  dx: "+str(dx)+" dy: "+str(dy))
        radius = self.tool.diameter/2.0
        for i in range(int(dy/radius)):
        #if True:
            #i = float(int(dy/radius)-10)
            line = ELine((left, top-i*radius), (right, top-i*radius), self.state.settings.get_def_lt())
            # try to find limiting element
            intersections = []
            lcu = line.get_cu()
            for e in self.offset_path:
                res = e.get_cu().find_intersection(lcu)
                #print res

                if res != None:
                    intersections+=res
            if len(intersections)>0:
                debug("  intersections:"+str(intersections))
                if len(intersections) == 1:
                    pass
                    # nleft = intersections[0]
                    # linear_pattern.append(ELine(nleft, line.end, settings.get_def_lt()))
                else:
                    while int(len(intersections)/2) > 0:
                        # find leftmost
                        nleft = min(intersections, key=lambda pt: pt[0])
                        intersections.remove(nleft)
                        nright = min(intersections, key=lambda pt: pt[0])
                        intersections.remove(nright)
                        linear_pattern.append(ELine(nleft, nright, self.state.settings.get_def_lt()))
        debug("  linear_pattern: "+str(linear_pattern))
        self.pocket_pattern = linear_pattern

    def apply(self, path):
        if path.operations[self.name]:
            if path.ordered_elements!=None:
                self.path = path
                #self.__build_offset_path(path)
                #self.__build_pocket_path()
                #self.draw_list = self.offset_path+self.pocket_pattern
                #self.draw_list = path.ordered_elements
                self.draw_list = self.build_points(path.ordered_elements)
                return True
        return False

    def get_gcode(self):
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        start = self.offset_path[0].start

        new_pos = [start[0], start[1], new_pos[2]]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth/(self.tool.diameter/2.0))+1):
            for e in self.offset_path:
                out += self.process_el_to_gcode(e, step)
            for e in self.pocket_pattern:
                out += self.process_el_to_gcode(e, step)
                

        new_pos = [new_pos[0], new_pos[1], self.tool.default_height]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out

    def __repr__(self):
        return "<Exact follow>"
