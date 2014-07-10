from state import state
from elements import *
from calc_utils import pt_to_pt_dist


class Path(object):
    def __init__(self, elements, name):
        self.elements = elements
        self.name = name

    def add_element(self, e):
        self.elements.append(e)

    def mk_connected_path(self):
        if len(self.elements)==0:
            return None
        available = self.elements[:]
        ce = [] # connected elements go here
        s = self.elements[0]
        ce.append(s)
        del available[0]
        while True:
            if len(available)==0:
                break
            cont = False
            current = ce[-1]
            min_dist = pt_to_pt_dist(available[0].start, current.end)
            min_dist_id = 0
            for i, e in enumerate(available):
                if not e.joinable:
                    continue
                dists = []
                dists.append(pt_to_pt_dist(e.start, current.end))
                dists.append(pt_to_pt_dist(e.end, current.start))
                dists.append(pt_to_pt_dist(e.end, current.end))
                dists.append(pt_to_pt_dist(e.start, current.start))
                md = min(dists)
                #print dists
                if md<min_dist:
                    min_dist = md
                    min_dist_id = i
            if (min_dist<0.001):
                ce.append(available[i])
                del available[i]
                cont = True

            if not cont:
                print "Ive tried hard, but still no success, so break"
                break

        if abs(ce[0].start[0]-ce[-1].end[0])<0.001 and abs(ce[0].start[1]-ce[-1].end[1])<0.001:
            pass # have to move joined path to separate subpath
        print "len(self.elements):", len(self.elements), "len(ce):", len(ce)
        if len(self.elements) == len(ce):
            return Path(ce, self.name+".sub")
        return None

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
