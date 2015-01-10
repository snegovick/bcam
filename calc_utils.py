import math

def rgb255_to_rgb1(rgb):
    return [rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0]

def sign(val):
    return (-1 if val<0 else 1)

def find_vect_normal(vect):
    n = [vect[1], -vect[0], 0]
    return n

def mk_vect(s, e):
    if len(e) == 3 and len(s) == 3:
        return [e[0]-s[0], e[1]-s[1], e[2]-s[2]]
    return [e[0]-s[0], e[1]-s[1], 0]

def normalize(v):
    if len(v) == 3:
        l = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        return [v[0]/l, v[1]/l, v[2]/l]

    l = math.sqrt(v[0]**2 + v[1]**2)
    return [v[0]/l, v[1]/l, 0]

def vect_sum(v1, v2):
    if len(v1) == 3 and len(v2) == 3:
        return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]
    return [v1[0]+v2[0], v1[1]+v2[1], 0]

def vect_len(v):
    if len(v) == 3:
        return math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return math.sqrt(v[0]**2+v[1]**2)

def scale_vect(v, factor):
    return map(lambda e: e*factor, v)

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
        return AABB(cx-r, cy-r, cx+r, cy+r)

    def distance_to_pt(self, pt):
        dist = pt_to_pt_dist(pt, self.center)-self.radius
        if self.uses_inner_space:
            return 0 if dist<0 else dist
        return abs(dist)

class PointUtils:
    def __init__(self, center):
        self.center = center

    def get_aabb(self):
        cx = self.center[0]
        cy = self.center[1]
        r = 1
        return AABB(cx-r, cy-r, cx+r, cy+r)

    def distance_to_pt(self, pt):
        dist = pt_to_pt_dist(pt, self.center)
        return abs(dist)

class ArcUtils:
    def __init__(self, center, radius, startangle, endangle, turnaround=False):
        self.ta = turnaround
        self.center = center
        self.radius = radius
        self.sa = startangle
        self.ea = endangle
        self.start = (self.center[0]+math.cos(self.sa)*self.radius, self.center[1]+math.sin(self.sa)*self.radius)
        self.end = (self.center[0]+math.cos(self.ea)*self.radius, self.center[1]+math.sin(self.ea)*self.radius)

    def get_aabb(self):
        x_min = min(self.start[0], self.end[0])
        y_min = min(self.start[1], self.end[1])
        x_max = max(self.start[0], self.end[0])
        y_max = max(self.start[1], self.end[1])

        return AABB(x_min, y_min, x_max, y_max)

    def __angledist(self, s, e):
        if s<0:
            s+=2*math.pi
        if e<0:
            e+=2*math.pi

        d = 0

        if e<s:
            d=(2*math.pi-s)+e
        else:
            d=e-s
        return d

    def check_angle_in_range(self, a):
        s = self.sa
        e = self.ea
        se_dist = self.__angledist(s, e)
        sa_dist = self.__angledist(s, a)
        ae_dist = self.__angledist(a, e)

        if sa_dist+ae_dist!=se_dist:
            return False
        return True

    def distance_to_pt(self, pt):
        a = math.atan2(pt[1]-self.center[1], pt[0]-self.center[0])
        print a, self.sa, self.ea
        if self.check_angle_in_range(a):
            dist = pt_to_pt_dist(pt, self.center)-self.radius
        else:
            dist = 1000
        return abs(dist)

    def get_normalized_start_normal(self):
        v = mk_vect(self.center, self.start)
        v = normalize(v)
        z_dir = [0, 0, -1]
        if self.ta:
            z_dir = [0, 0, 1]
        v_dir = [z_dir[2]*v[1], -v[0]*z_dir[2], 0]
        v_dir = normalize(v_dir)
        
        return find_vect_normal(v_dir)

    def get_normalized_end_normal(self):
        return self.get_normalized_start_normal()

    def check_if_pt_belongs(self, pt):
        v = mk_vect(pt, self.center)
        if abs((self.radius) - vect_len(v))>0.001:
            #print "radius check failed"
            return False

        a = math.atan2(pt[1]-self.center[1], pt[0]-self.center[0])
        if (self.check_angle_in_range(a)):
            #print "radius and angle ok"
            return True
        return False

    def find_intersection(self, other_element):
        oe = other_element
        if other_element.__class__.__name__ == "LineUtils":
            #print "line to arc"
            dx = oe.end[0] - oe.start[0]
            dy = oe.end[1] - oe.start[1]
            dr = math.sqrt(dx**2 + dy**2)
            d = oe.start[0]*oe.end[1] - oe.start[1]*oe.end[0]
            desc = ((self.radius)**2)*dr**2 - d**2
            intersections = []
            if desc == 0:
                #single point
                #print "single point"
                x_i = (d*dy+sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i = (-d*dx+abs(dy)*math.sqrt(desc))/(dr**2)
                intersections.append((x_i, y_i))
            elif desc > 0:
                #intersection
                #print "intersection"
                x_i1 = (d*dy+sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i1 = (-d*dx+abs(dy)*math.sqrt(desc))/(dr**2)
                x_i2 = (d*dy-sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i2 = (-d*dx-abs(dy)*math.sqrt(desc))/(dr**2)
                intersections.append((x_i1, y_i1))
                intersections.append((x_i2, y_i2))
            else:
                #no intersection
                #print "no intersection"
                return None
            #check whether intersections are inside existing element sections
            checked_intersections = []
            for pt in intersections:
                if oe.check_if_pt_belongs(pt):
                    #print "oe belongs"
                    if self.check_if_pt_belongs(pt):
                        #print "self belongs"
                        checked_intersections.append(pt)
                    else:
                        #print "self failed"
                        pass
                else:
                    #print "oe failed"
                    pass
            if len(checked_intersections)>0:
                return checked_intersections
        else:
            print "A: Not calc util:", other_element.__class__.__name__
        return None


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

    def check_if_pt_belongs(self, pt):
        x_i, y_i = pt

        minx = min(self.start[0], self.end[0])
        maxx = max(self.start[0], self.end[0])
        miny = min(self.start[1], self.end[1])
        maxy = max(self.start[1], self.end[1])

        #print "s:", (minx, miny), "e:", (maxx, maxy)

        x_intersects = False
        y_intersects = False

        if abs(minx-maxx)<0.001:
            if abs(x_i-minx)<0.001:
                x_intersects = True
                #print "dx=0"
            else:
                return False
        elif x_i>=minx and x_i<=maxx:
            x_intersects = True
        
        if abs(miny-maxy)<0.001:
            if abs(y_i-miny)<0.001:
                y_intersects = True
                #print "dy=0"
            else:
                return False
        elif y_i>=miny and y_i<=maxy:
            y_intersects = True

        if x_intersects and y_intersects:
            return True

        return False

    def find_intersection(self, other_element):
        oe = other_element
        #print oe
        if other_element.__class__.__name__ == "LineUtils":
            #print "line to line"
            # line to line intersection
            ms, me = self.start, self.end

            ma = me[1]-ms[1]
            mb = ms[0]-me[0]
            mc = ma*ms[0]+mb*ms[1]

            ms, me = oe.start, oe.end
            oa = me[1]-ms[1]
            ob = ms[0]-me[0]
            oc = oa*ms[0]+ob*ms[1]

            det = float(ma*ob - oa*mb)
            if det == 0:
                # lines are parallel
                #print "parallel"
                return None
            else:
                x_i = (ob*mc-mb*oc)/det
                y_i = (ma*oc-oa*mc)/det
                #print "int:", x_i, y_i
                if self.check_if_pt_belongs((x_i, y_i)):
                    #print "on self"
                    if oe.check_if_pt_belongs((x_i, y_i)):
                        #print "on oe"
                        return [(x_i, y_i),]
                    else:
                        #print "not on oe"
                        #print "int:", x_i, y_i
                        #print "oe:", oe.start, oe.end
                        pass
                else:
                    pass
                    #print "not on self"
        elif other_element.__class__.__name__ == "ArcUtils":
            #print "arc to line"
            return oe.find_intersection(self)
        else:
            print "L: Not calc util:", other_element.__class__.__name__

        return None

    def get_normalized_start_normal(self):
        v = mk_vect(self.start, self.end)
        vn = normalize(v)
        return find_vect_normal(vn)

    def get_normalized_end_normal(self):
        v = mk_vect(self.start, self.end)
        vn = normalize(v)
        return find_vect_normal(vn)

    def __reproject_pt(self, pt, sina, cosa):
        return (pt[0]*cosa-pt[1]*sina, pt[0]*sina+pt[1]*cosa)

if __name__=="__main__":
    au = ArcUtils((0, 0), 1, -10*math.pi/180.0, 300*math.pi/180.0)
    
    angle = 90
    print "checking angle", angle, au.check_angle_in_range(angle*math.pi/180.0)
    angle = 190
    print "checking angle", angle, au.check_angle_in_range(angle*math.pi/180.0)
    angle = -15
    print "checking angle", angle, au.check_angle_in_range(angle*math.pi/180.0)
    angle = 290
    print "checking angle", angle, au.check_angle_in_range(angle*math.pi/180.0)
    angle = 301
    print "checking angle", angle, au.check_angle_in_range(angle*math.pi/180.0)
