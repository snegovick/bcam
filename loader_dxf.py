import loader
from path import ELine, EArc, ECircle, Path
from settings import settings

import dxfgrabber

class DXFEnum:
    line = "LINE"
    arc = "ARC"
    circle = "CIRCLE"
    insert = "INSERT"

class DXFLoader(loader.SourceLoader):
    def __init__(self):
        pass

    def __basic_el(self, e, p, offset):

        if e.dxftype == DXFEnum.line:
            #print "line"
            if offset !=None:
                start = [offset[0], offset[1]]
                end = [offset[0], offset[1]]
            else:
                start = [0,0]
                end = [0,0]

            start[0]+=e.start[0]
            start[1]+=e.start[1]
            end[0]+=e.end[0]
            end[1]+=e.end[1]

            el = ELine(tuple(start), tuple(end), settings.get_def_lt())
            p.add_element(el)
        elif e.dxftype == DXFEnum.arc:
            #print "arc"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]
            el = EArc(tuple(center[:2]), e.radius, e.startangle, e.endangle, settings.get_def_lt())
            p.add_element(el)
        elif e.dxftype == DXFEnum.circle:
            #print "circle"
            if offset != None:
                center = [offset[0], offset[1]]
            else:
                center = [0,0]
            center[0] += e.center[0]
            center[1] += e.center[1]

            el = ECircle(tuple(center[:2]), e.radius, settings.get_def_lt())
            p.add_element(el)
        else:
            return False
        return True

    def __is_basic(self, e):
        if e.dxftype == DXFEnum.line or e.dxftype == DXFEnum.arc or e.dxftype == DXFEnum.circle:
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
        p = Path([], "ungrouped", settings.get_def_lt())
        for e in entities:
            if self.__is_basic(e):
                self.__basic_el(e, p, None)
            elif e.dxftype == DXFEnum.insert:
                block_name = e.name
                offset = e.insert[:2]
                tp = Path([], block_name, settings.get_def_lt())
                for b in dxf.blocks:
                    if b.name == block_name:
                        for e in b:
                            if self.__is_basic(e):
                                self.__basic_el(e, p, offset)
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
