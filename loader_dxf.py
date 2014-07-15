import loader
from path import ELine, EArc, ECircle, Path
from settings import settings

import dxfgrabber

class DXFEnum:
    line = "LINE"
    arc = "ARC"
    circle = "CIRCLE"

class DXFLoader(loader.SourceLoader):
    def __init__(self):
        pass

    def load(self, path):
        dxf = dxfgrabber.readfile(path)
        print("DXF version: {}".format(dxf.dxfversion))
        header_var_count = len(dxf.header) # dict of dxf header vars
        layer_count = len(dxf.layers) # collection of layer definitions
        block_definition_count = len(dxf.blocks) #  dict like collection of block definitions
        entity_count = len(dxf.entities) # list like collection of entities
        #print dxf.entities
        blocks = dxf.blocks
        de = DXFEnum()
        paths = []
        all_entities = [entity for entity in dxf.entities]

        p = Path([], "source", settings.get_def_lt())
        for e in all_entities:
            if e.dxftype == de.line:
                el = ELine(tuple(e.start[:2]), tuple(e.end[:2]), settings.get_def_lt())
                p.add_element(el)
            elif e.dxftype == de.arc:
                el = EArc(tuple(e.center[:2]), e.radius, e.startangle, e.endangle, settings.get_def_lt())
                p.add_element(el)
            elif e.dxftype == de.circle:
                el = ECircle(tuple(e.center[:2]), e.radius, settings.get_def_lt())
                p.add_element(el)
            else:
                print "Unknown type:", e.dxftype
        paths.append(p)
            #print "Trying to connect path:"
            #print p.mk_connected_path()
        print p.elements
        return paths
