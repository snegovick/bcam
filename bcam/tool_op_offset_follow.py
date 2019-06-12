from __future__ import absolute_import, division, print_function

import math
from bcam.tool_operation import ToolOperation, TOEnum
from bcam.tool_abstract_follow import TOAbstractFollow
from bcam.generalized_setting import TOSetting
from bcam.calc_utils import (find_vect_normal, mk_vect, normalize, vect_sum,
                             vect_len, scale_vect, pt_to_pt_dist)
from bcam.elements import ELine, EArc, ECircle
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname


import cairo
import json

class TOOffsetFollow(TOAbstractFollow):
    def __init__(self, state, depth=0, index=0, offset=0, data=None):
        super(TOAbstractFollow, self).__init__(state)
        self.state = state
        self.name = TOEnum.offset_follow
        if data == None:
            self.index = index
            self.depth = depth
            self.offset = offset
            self.path = None
            self.offset_path = None
        else:
            self.deserialize(data)

        self.display_name = TOEnum.offset_follow+" "+str(self.index)

    def serialize(self):
        return {'type': 'tooffsetfollow', 'path_ref': self.path.name, 'depth': self.depth, 'index': self.index, 'offset': self.offset}

    def deserialize(self, data):
        self.depth = data["depth"]
        self.index = data["index"]
        self.offset = data["offset"]

        p = self.try_load_path_by_name(data["path_ref"], Singleton.state)
        if p:
            self.apply(p)

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, Singleton.state.settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),
                        TOSetting("float", None, None, self.offset, "Offset, mm: ", self.set_offset_s)]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def set_offset_s(self, setting):
        self.offset = setting.new_value
        self.offset_path = self.__build_offset_path(self.path)
        self.draw_list = self.offset_path

    def __remove_intersected_parts(self, p):
        dbgfname()
        return p

    def __build_offset_path(self, p):
        dbgfname()
        offset_path = self.__build_offset_path_normals(p)
        debug("  checking offset path")
        if (offset_path != None):
            out = self.__remove_intersected_parts(offset_path)
            return out
        debug("  offset path is None")
        return None

    def __two_point_offset(self, prev, next):
        dbgfname()
        nsc = next.start
        nec = next.end
        sc = prev.start
        ec = prev.end
        
        nnsn = next.get_normalized_start_normal()
        nen = prev.get_normalized_end_normal()

        e_s_pt = [nen[0]*self.offset+sc[0], nen[1]*self.offset+sc[1], 0]
        e_e_pt = [nen[0]*self.offset+ec[0], nen[1]*self.offset+ec[1], 0]
        ne_s_pt = [nnsn[0]*self.offset+nsc[0], nnsn[1]*self.offset+nsc[1], 0]
        ne_e_pt = [nnsn[0]*self.offset+nec[0], nnsn[1]*self.offset+nec[1], 0]
        
        ne_dy = ne_e_pt[1]-ne_s_pt[1]
        ne_dx = ne_e_pt[0]-ne_s_pt[0]
        
        e_dy = e_e_pt[1]-e_s_pt[1]
        e_dx = e_e_pt[0]-e_s_pt[0]
        
        if ((e_dx == 0) and (ne_dy == 0)):
            x = e_e_pt[0]
            y = ne_e_pt[1]
            debug("  case 1, x: "+str(x)+" y: "+str(y))
        elif((e_dy == 0) and (ne_dx == 0)):
            x = ne_e_pt[0]
            y = e_e_pt[1]
            debug("  case 2, x: "+str(x)+" y: "+str(y))
        elif (((e_dy == 0) and (ne_dy == 0)) or ((e_dx == 0) and (ne_dx == 0))): #parallel lines
            x = e_e_pt[0]
            y = e_e_pt[1]
        else:
            a = (ne_e_pt[0]*ne_s_pt[1]-ne_s_pt[0]*ne_e_pt[1])
            b = (e_e_pt[0]*e_s_pt[1]-e_s_pt[0]*e_e_pt[1])

            debug("  a: "+str(a)+" b: "+str(b)+" e_dx: "+str(e_dx)+" e_dy: "+str(e_dy)+" ne_dx: "+str(ne_dx)+" ne_dy: "+str(ne_dy))
            
            x = (a*e_dx-b*ne_dx)/(e_dy*ne_dx-ne_dy*e_dx)
            if e_dx == 0:
                y = (x*ne_dy+a)/ne_dx
            else:
                y = (x*e_dy+b)/e_dx
            debug("  case 3, x: "+str(x)+" y: "+str(y))
        e_pt = [x, y]
        return e_pt

    def __build_offset_path_normals(self, p):
        dbgfname()
        new_elements = []
        elements = p.get_ordered_elements()
        if len(elements)==0:
            return None
        if len(elements)==1:
            e = elements[0]
            if type(e).__name__ == "ECircle":
                new_elements.append(ECircle(e.center, e.radius+self.offset, e.lt, e.color, None))
            elif type(e).__name__ == "ELine":
                el = elements[0]
                s = el.start
                e = el.end
                nsn = elements[0].get_normalized_start_normal()
                s_pt = [nsn[0]*self.offset+s[0], nsn[1]*self.offset+s[1], 0]
                e_pt = [nsn[0]*self.offset+e[0], nsn[1]*self.offset+e[1], 0]
                ne = ELine(s_pt, e_pt, el.lt, el.color)
                new_elements.append(ne)
        else:            
            s = elements[0].start
            e = elements[0].end
            nsn = elements[0].get_normalized_start_normal()
            s_pt = [nsn[0]*self.offset+s[0], nsn[1]*self.offset+s[1], 0]
            #preprocess, convert arcs to sequencies of lines
            converted_elements = []
            for i, e in enumerate(elements):
                if type(e).__name__ == "EArc":
                    sa = e.startangle
                    ea = e.endangle
                    if sa > ea:
                        ea+=math.pi*2
                    da = (ea - sa)

                    
                    n_steps = int(da/0.1)
                    s_pt = (e.center[0]+math.cos(sa)*e.radius, e.center[1]+math.sin(sa)*e.radius)
                    debug("  splitting arc, start angle: "+str(sa)+" start_pt: "+str(s_pt))
                    for i in range(1,n_steps):
                        a = sa+i*0.1
                        e_pt = (e.center[0]+math.cos(a)*e.radius, e.center[1]+math.sin(a)*e.radius)
                        ne = ELine(s_pt, e_pt, e.lt, e.color)
                        debug("  angle: "+str(a)+" line: "+str(s_pt)+" "+str(e_pt))
                        s_pt = e_pt
                        converted_elements.append(ne)
                    e_pt = e.end
                    ne = ELine(s_pt, e_pt, e.lt, e.color)
                    converted_elements.append(ne)
                else:
                    converted_elements.append(e)

            elements = converted_elements
            s_pt = None
            #s_pt = [nsn[0]*self.offset+s[0], nsn[1]*self.offset+s[1], 0]

            for i, e in enumerate(elements):
                sc = e.start # current start
                ec = e.end # current end


                if s_pt == None:
                    if pt_to_pt_dist(sc, elements[-1].end)<0.001:
                        debug("  s_pt")
                        s_pt = self.__two_point_offset(elements[-1], e)
                    else:
                        nsn = e.get_normalized_start_normal()
                        #n = vect_sum(nsn, nen) # sum of new start normal and prev end normal
                        n = nsn
                        shift = sc
                        s_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]

                if i<len(elements)-1:
                    e_pt = self.__two_point_offset(e, elements[i+1])
                else:
                    nen = e.get_normalized_end_normal()
                    n = nen
                    if pt_to_pt_dist(ec, elements[0].start)<0.001:
                        e_pt = self.__two_point_offset(e, elements[0])
                    else:
                        shift = ec
                        e_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]
                if type(e).__name__ == "ELine":
                    ne = ELine(s_pt, e_pt, e.lt, e.color)
                elif type(e).__name__ == "EArc":
                    ne = EArc(center=e.center, lt=e.lt, start=s_pt, end=e_pt, color=e.color)

                new_elements.append(ne)
                s_pt = e_pt
                e_pt = None
        offset_path = new_elements
        debug("  offset_path: "+str(offset_path))
        return offset_path

    def apply(self, path):
        dbgfname()
        debug("  apply path: "+str(path))
        if path.operations[self.name]:
            debug("  path ordered elements: "+str(path.ordered_elements))
            if path.ordered_elements!=None:
                self.path = path
                self.offset_path = self.__build_offset_path(path)
                self.draw_list = self.offset_path
                return True
        return False

    def get_gcode(self):
        return self.get_gcode_base(self.draw_list)

    def __repr__(self):
        return "<Offset follow>"
