from state import state
from elements import *
from calc_utils import pt_to_pt_dist
from tool_operation import TOEnum
from settings import settings


class Path(Element):
    def __init__(self, elements, name, lt):
        super(Path, self).__init__(lt)
        self.display = True
        self.elements = elements
        self.name = name
        self.ordered_elements = []
        self.operations[TOEnum.exact_follow] = True
        self.operations[TOEnum.offset_follow] = True
        self.operations[TOEnum.pocket] = True

    def add_element(self, e):
        self.elements.append(e)

    def __find_adjacent_element(self, current, available, direction_fwd=True):
        min_dist = pt_to_pt_dist(available[0].start, current.end)
        min_dist_id = 0
        min_order = {"turnaround": False, "offset": 1}
        for i, e in enumerate(available):
            orders = []
            dists = []
            if direction_fwd:
                dists.append(pt_to_pt_dist(e.start, current.end))
                orders.append({"turnaround": False, "offset": 1})
                orders.append({"turnaround": True, "offset": 1})
                dists.append(pt_to_pt_dist(e.start, current.start))
            else:
                dists.append(pt_to_pt_dist(e.end, current.start))
                orders.append({"turnaround": False, "offset": -1})
                dists.append(pt_to_pt_dist(e.end, current.end))
                orders.append({"turnaround": True, "offset": -1})
            md = min(dists)
            #print dists
            if md<min_dist:
                min_dist = md
                min_dist_id = i
                min_order = orders[dists.index(md)]
                #print "md, i:", md, i
        return min_dist, min_dist_id, min_order

    def __append_element(self, min_dist_id, min_order, available, ordered_elements, ce):
        i = min_dist_id
        ce.append(available[i])
        if min_order["offset"] == 1:
            if min_order["turnaround"] == False:
                available[i].start = ordered_elements[-1].end
                ordered_elements.append(available[i])
            else:
                available[i].end = ordered_elements[-1].end
                ordered_elements.append(available[i].turnaround())
        else:
            if min_order["turnaround"] == False:
                available[i].end = ordered_elements[0].start
                ordered_elements.insert(0, available[i])
            else:
                available[i].start = ordered_elements[0].start
                ordered_elements.insert(0, available[i].turnaround())
        del available[i]


    def mk_connected_path(self):
        if len(self.elements)==0:
            return None

        if not self.elements[0].joinable:
            p = Path([self.elements[0]], self.name+".path", settings.get_def_lt())
            p.ordered_elements = [self.elements[0]]
            return p
        available = self.elements[:]
        ce = [] # connected elements go here

        not_joinables = []
        for i, e in enumerate(available):
            if not e.joinable:
                not_joinables.append(i)

        not_joinables.reverse()
        for nj in not_joinables:
            del available[nj]

        available_len = len(available)

        if available_len==0:
            return None

        #find first joinable
        self.order = [0]
        ce.append(available[0])
        ordered_elements = [available[0]]
        del available[0]

        while True:
            if len(available)==0:
                break
            cont = False
            current = (ce[-1], ce[0])
            min_dist, min_dist_id, min_order = self.__find_adjacent_element(current[0], available)
            if (min_dist<0.001):
                
                self.__append_element(min_dist_id, min_order, available, ordered_elements, ce)
                cont = True
            if not cont:
                min_dist, min_dist_id, min_order = self.__find_adjacent_element(current[1], available, False)
                if (min_dist<0.001):
                    self.__append_element(min_dist_id, min_order, available, ordered_elements, ce)
                    cont = True

            if not cont:
                print "Ive tried hard, but still no success, so break"
                break

        if abs(ce[0].start[0]-ce[-1].end[0])<0.001 and abs(ce[0].start[1]-ce[-1].end[1])<0.001:
            pass # have to move joined path to separate subpath
        print "available len", available_len, "len(ce):", len(ce)
        print available
        #if available_len == len(ce):
        p = Path(ce, self.name+".sub", settings.get_def_lt())
        p.ordered_elements = ordered_elements
        return p

    def set_closed(self):
        self.closed = True

    def get_closed(self):
        return self.closed

    def draw(self, ctx, offset):
        if self.display:
            ctx.translate(offset[0], offset[1])
            ctx.scale(state.scale[0], state.scale[1])
            for e in self.elements:
                e.draw(ctx)
            ctx.identity_matrix()
