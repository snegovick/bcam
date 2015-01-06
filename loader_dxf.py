import loader
from calc_utils import rgb255_to_rgb1
from path import ELine, EArc, ECircle, Path
from state import state

import dxfgrabber

color_white = [255, 255, 255]
default_color = color_white

class DXFEnum:
    line = "LINE"
    arc = "ARC"
    circle = "CIRCLE"
    insert = "INSERT"
    polyline = "POLYLINE"

class DXFLoader(loader.SourceLoader):
    def __init__(self):
        pass

    def __mk_line(self, s, e, offset):
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

        return ELine(tuple(start), tuple(end), state.settings.get_def_lt())

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
            el = self.__mk_line(e.start, e.end, offset)
            el.color = color
            p.add_element(el)
        elif e.dxftype == DXFEnum.arc:
            #print "arc"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]
            el = EArc(tuple(center[:2]), e.radius, e.startangle, e.endangle, state.settings.get_def_lt())
            el.color = color
            p.add_element(el)
        elif e.dxftype == DXFEnum.circle:
            #print "circle"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]

            el = ECircle(tuple(center[:2]), e.radius, state.settings.get_def_lt())
            el.color = color
            p.add_element(el)
        elif e.dxftype == DXFEnum.polyline:
            start = None
            for pt in e.points:
                end = pt
                if start == None:
                    start = pt

                else:
                    el = self.__mk_line(start, end, offset)
                    el.color = color
                    p.add_element(el)
                start = end
                
        else:
            return False
        return True

    def __is_basic(self, e):
        if e.dxftype == DXFEnum.line or e.dxftype == DXFEnum.arc or e.dxftype == DXFEnum.circle or e.dxftype == DXFEnum.polyline:
            return True
        return False

    def load(self, path):
        dxf = dxfgrabber.readfile(path)
        print("DXF version: {}".format(dxf.dxfversion))
        header_var_count = len(dxf.header) # dict of dxf header vars
        layer_count = len(dxf.layers) # collection of layer definitions
        block_definition_count = len(dxf.blocks) #  dict like collection of block definitions
        entity_count = len(dxf.entities) # list like collection of entities
        blocks = dxf.blocks
        paths = []
        entities = [e for e in dxf.entities]
        p = Path(state, [], "ungrouped", state.settings.get_def_lt().name)
        for e in entities:
            if self.__is_basic(e):
                self.__basic_el(e, p, None, dxf.layers, None)
            elif e.dxftype == DXFEnum.insert:
                block_name = e.name
                offset = e.insert[:2]
                tp = Path(state, [], block_name, state.settings.get_def_lt().name)
                for b in dxf.blocks:
                    if b.name == block_name:
                        for e in b:
                            if self.__is_basic(e):
                                self.__basic_el(e, p, offset, dxf.layers, b)
                            else:
                                print "Unknown type:", e.dxftype
                                print e
                paths.append(tp)
            else:
                print "Unknown type:", e.dxftype
                print e
        if len(p.elements)>0:
            paths.append(p)

        return paths
