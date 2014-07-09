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

    
class CircleUtils:
    def __init__(self, center, radius, uses_inner_space=False):
        self.center = center
        self.radius = radius
        self.uses_inner_space=uses_inner_space

    def distance_to_pt(self, pt):
        dist = math.sqrt((pt[0]-self.center[0])**2 + (pt[1]-self.center[1])**2)-self.radius
        if self.uses_inner_space:
            return 0 if dist<0 else dist
        return abs(dist)
