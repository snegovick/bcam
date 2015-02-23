from __future__ import absolute_import, division

from bcam import loader
from bcam.calc_utils import rgb255_to_rgb1
from bcam.path import ELine, EArc, ECircle, EPoint, Path
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

import dxfgrabber

color_white = [255, 255, 255]
default_color = color_white

class DXFEnum:
    line = "LINE"
    arc = "ARC"
    circle = "CIRCLE"
    insert = "INSERT"
    polyline = "POLYLINE"
    point = "POINT"

class DXFLoader(loader.SourceLoader):
    def __init__(self):
        pass

    def __mk_line(self, s, e, offset, color):
        if offset !=None:
            start = [offset[0], offset[1]]
            end = [offset[0], offset[1]]
        else:
            start = [0,0]
            end = [0,0]
            
        start[0]+=s[0]
        start[1]+=s[1]
        end[0]+=e[0]
        end[1]+=e[1]

        return ELine(tuple(start), tuple(end), Singleton.state.settings.get_def_lt(), color)

    def __basic_el(self, e, p, offset, layers, block):
        layer = layers[e.layer]
        color = None
        if e.color == dxfgrabber.BYLAYER:
            color = layer.color
        elif e.color == dxfgrabber.BYBLOCK:
            if (block != None):
                color = block.color
            else:
                color = layer.color
        else:
            color = e.color

        color = rgb255_to_rgb1(dxfgrabber.color.TrueColor.from_aci(color).rgb())
        if e.dxftype == DXFEnum.line:
            #print "line"
            el = self.__mk_line(e.start, e.end, offset, color)
            p.add_element(el)
        elif e.dxftype == DXFEnum.arc:
            #print "arc"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]
            el = EArc(tuple(center[:2]), e.radius, e.startangle, e.endangle, Singleton.state.settings.get_def_lt(), color=color)
            p.add_element(el)
        elif e.dxftype == DXFEnum.circle:
            #print "circle"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]

            el = ECircle(tuple(center[:2]), e.radius, Singleton.state.settings.get_def_lt(), color)
            p.add_element(el)
        elif e.dxftype == DXFEnum.point:
            #print "circle"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.point[0]
            center[1] += e.point[1]

            el = EPoint(tuple(center[:2]), Singleton.state.settings.get_def_lt(), color)
            p.add_element(el)
        elif e.dxftype == DXFEnum.polyline:
            start = None
            for pt in e.points:
                end = pt
                if start == None:
                    start = pt

                else:
                    el = self.__mk_line(start, end, offset, color)
                    p.add_element(el)
                start = end
                
        else:
            return False
        return True

    def __is_basic(self, e):
        if e.dxftype == DXFEnum.line or e.dxftype == DXFEnum.arc or e.dxftype == DXFEnum.circle or e.dxftype == DXFEnum.polyline or e.dxftype == DXFEnum.point:
            return True
        return False

    def load(self, path):
        dbgfname()
        dxf = dxfgrabber.readfile(path)
        debug("  DXF version: {}".format(dxf.dxfversion))
        header_var_count = len(dxf.header) # dict of dxf header vars
        layer_count = len(dxf.layers) # collection of layer definitions
        block_definition_count = len(dxf.blocks) #  dict like collection of block definitions
        entity_count = len(dxf.entities) # list like collection of entities
        blocks = dxf.blocks
        paths = []
        entities = [e for e in dxf.entities]
        p = Path(Singleton.state, [], "ungrouped", Singleton.state.settings.get_def_lt().name)
        for e in entities:
            if self.__is_basic(e):
                self.__basic_el(e, p, None, dxf.layers, None)
            elif e.dxftype == DXFEnum.insert:
                block_name = e.name
                offset = e.insert[:2]
                tp = Path(Singleton.state, [], block_name, Singleton.state.settings.get_def_lt().name)
                for b in dxf.blocks:
                    if b.name == block_name:
                        for e in b:
                            if self.__is_basic(e):
                                self.__basic_el(e, p, offset, dxf.layers, b)
                            else:
                                debug("  Unknown type: "+str(e.dxftype))
                                debug("  "+str(e))
                paths.append(tp)
            else:
                debug("  Unknown type: "+str(e.dxftype))
                debug("  "+str(e))
        if len(p.elements)>0:
            paths.append(p)

        return paths
