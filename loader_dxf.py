import loader
from path import ELine, Path

import dxfgrabber

class DXFEnum:
    line = "LINE"

class DXFLoader(loader.SourceLoader):
    def __init__(self):
        pass

    def load(self, path):
        dxf = dxfgrabber.readfile(path)
        print("DXF version: {}".format(dxf.dxfversion))
        header_var_count = len(dxf.header) # dict of dxf header vars
        layer_count = len(dxf.layers) # collection of layer definitions
        block_definition_count = len(dxf.blocks) #  dict like collection of block definitions
        entitiy_count = len(dxf.entities) # list like collection of entities
        print dxf.entities
        blocks = dxf.blocks
        de = DXFEnum()
        paths = []
        for b in blocks:
            p = Path([], b.name)
            for e in b:
                if e.dxftype == de.line:
                    el = ELine(tuple(e.start[:2]), tuple(e.end[:2]))
                    p.add_element(el)
            print p.elements
            paths.append(p)
        return paths
            
