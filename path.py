from state import state
from elements import *


class Path(object):
    def __init__(self, elements, name):
        self.elements = elements
        self.name = name

    def add_element(self, e):
        self.elements.append(e)

    def mk_connected_path(self):
        if len(self.elements)==0:
            return False
        ce = [] # connected elements go here
        s = self.elements[0]
        ce.append(s)
        while True:
            cont = False
            current = ce[-1]
            for e in self.elements:
                if not e.joinable:
                    continue

                if e not in ce:
                    if abs(e.start[0]-current.end[0])<0.001 and abs(e.start[1]-current.end[1])<0.001:
                        ce.append(e)
                        cont = True
                        break

            if not cont:
                print "havent found next for", current
                break

        if abs(ce[0].start[0]-ce[-1].end[0])<0.001 and abs(ce[0].start[1]-ce[-1].end[1])<0.001:
            pass # have to move joined path to separate subpath
        if len(self.elements) == len(ce):
            self.elements = ce
            return True
        return False

    def set_closed(self):
        self.closed = True

    def get_closed(self):
        return self.closed

    def draw(self, ctx, offset):
        ctx.translate(offset[0], offset[1])
        ctx.scale(state.scale[0], state.scale[1])
        for e in self.elements:
            e.draw(ctx)
        ctx.identity_matrix()
