import math

class OverlapEnum:
    fully_covers = 1
    partially_overlap = 2
    fully_lays_inside = 3
    no_overlap = 4

class AABB:
    def __init__(self, sx, sy, ex, ey):
        print sx, sy, ex, ey
        self.left = min(sx, ex)
        self.right = max(sx, ex)
        self.top = max(sy, ey)
        self.bottom = min(sy, ey)

    def point_in_aabb(self, pt):
        x = pt[0]
        y = pt[1]
        
        if (x>=self.left and x<=self.right and y>=self.bottom and y<=self.top):
            return True
        return False

    def aabb_in_aabb(self, box, check_inside_overlap=True):
        lt = False
        lb = False
        rt = False
        rb = False

        if self.point_in_aabb((box.left, box.top)):
            lt = True
        if self.point_in_aabb((box.left, box.bottom)):
            lb = True
        if self.point_in_aabb((box.right, box.bottom)):
            rb = True
        if self.point_in_aabb((box.right, box.top)):
            rt = True
            
        oe = OverlapEnum
        if lt and lb and rt and rb:
            return OverlapEnum.fully_covers
        elif lt or lb or rt or rb:
            return OverlapEnum.partially_overlap
        if check_inside_overlap:
            if box.aabb_in_aabb(self, False)==OverlapEnum.fully_covers:
                return OverlapEnum.fully_lays_inside
        return OverlapEnum.no_overlap
        
    def __repr__(self):
        return "AABB (l: %f r: %f t: %f b: %f)" % (self.left, self.right, self.top, self.bottom)


def pt_to_pt_dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

class CircleUtils:
    def __init__(self, center, radius, uses_inner_space=False):
        self.center = center
        self.radius = radius
        self.uses_inner_space=uses_inner_space

    def get_aabb(self):
        cx = self.center[0]
        cy = self.center[1]
        r = self.radius
        return AABB(cx-r, cy-r, cx+3, cy+r)

    def distance_to_pt(self, pt):
        dist = pt_to_pt_dist(pt, self.center)-self.radius
        if self.uses_inner_space:
            return 0 if dist<0 else dist
        return abs(dist)

class ArcUtils:
    def __init__(self, center, radius, startangle, endangle):
        self.center = center
        self.radius = radius
        self.sa = startangle
        self.ea = endangle
        self.start = (self.center[0]+math.cos(self.sa)*self.radius, self.center[1]+math.sin(self.sa)*self.radius)
        self.end = (self.center[0]+math.cos(self.ea)*self.radius, self.center[1]+math.sin(self.ea)*self.radius)

    def get_aabb(self):
        x_min = min(self.start[0], self.end[0], self.center[0])
        y_min = min(self.start[1], self.end[1], self.center[1])
        x_max = max(self.start[0], self.end[0], self.center[0])
        y_max = max(self.start[1], self.end[1], self.center[1])

        return AABB(x_min, y_min, x_max, y_max)

    def distance_to_pt(self, pt):
        a = math.atan2(pt[1]-self.center[1], pt[0]-self.center[0])
        print a, self.sa, self.ea
        if a>=self.sa and a<=self.ea:
            dist = pt_to_pt_dist(pt, self.center)-self.radius
        elif a<self.sa:
            dist = pt_to_pt_dist(pt, self.start)
        elif a>self.ea:
            dist = pt_to_pt_dist(pt, self.end)
        return abs(dist)

class LineUtils:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_aabb(self):
        return AABB(self.start[0], self.start[1], self.end[0], self.end[1])

    def distance_to_pt(self, pt):
        dist = 0
        a = math.atan2(self.start[1]-self.end[1], self.start[0]-self.end[0])
        #print "alpha:", a
        sina = math.sin(a)
        cosa = math.cos(a)
        s = self.__reproject_pt(self.start, sina, cosa)
        #s = self.start
        e = self.__reproject_pt(self.end, sina, cosa)
        p = self.__reproject_pt(pt, sina, cosa)
        left = min(s[0], e[0])
        right = max(s[0], e[0])
        if p[0]<=left:
            dist = pt_to_pt_dist(p, (left, s[1]))
            return dist
        elif p[0]>=right:
            dist = pt_to_pt_dist(p, (right, s[1]))
            return dist
        a = pt_to_pt_dist(s, e) #abs(s[0]-e[0])
        b = pt_to_pt_dist(s, p)
        c = pt_to_pt_dist(e, p)
        p = (a+b+c)/2.0
        #print "a:", a, "b:", b, "c:", c, "p:", p, p*(p-a)*(p-b)*(p-c)
        dist = abs(math.sqrt(p*(p-a)*(p-b)*(p-c))*2/a)
        #print "dist:" , dist
        return dist

    def __reproject_pt(self, pt, sina, cosa):
        return (pt[0]*cosa-pt[1]*sina, pt[0]*sina+pt[1]*cosa)
