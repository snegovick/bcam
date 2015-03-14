from __future__ import absolute_import, division, print_function

import math
from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

def transform_pt(pt, angle):
    out = [0,0]
    cos = math.cos(angle)
    sin = math.sin(angle)
    out[0] = pt[0]*cos - pt[1]*sin
    out[1] = pt[0]*sin + pt[1]*cos
    return out

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

def vect_mul_const(v, c):
    return [v[0]*c, v[1]*c]

def vect_sub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1]]

def vect_len(v):
    if len(v) == 3:
        return math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return math.sqrt(v[0]**2+v[1]**2)

def vect_len2(v):
    if len(v) == 3:
        return v[0]**2+v[1]**2+v[2]**2
    return v[0]**2+v[1]**2


def scale_vect(v, factor):
    return map(lambda e: e*factor, v)

def dot_product(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1]

def linearized_path_aabb(path):
    xmin = path[0].start[0]
    xmax = path[0].start[0]
    ymin = path[0].start[1]
    ymax = path[0].start[1]

    for e in path:
        sx = e.start[0]
        sy = e.start[1]
        ex = e.end[0]
        ey = e.end[1]
        
        xmax_se = max(sx, ex)
        xmin_se = min(sx, ex)
        ymax_se = max(sy, ey)
        ymin_se = min(sy, ey)

        if (xmin_se < xmin):
            xmin = xmin_se

        if (ymin_se < ymin):
            ymin = ymin_se

        if (xmax_se > xmax):
            xmax = xmax_se

        if (ymax_se > ymax):
            ymax = ymax_se

    return AABB(xmin, ymin, xmax, ymax)

def find_center_of_mass(path):
    x = path[0].start[0]
    y = path[0].start[1]
    for e in path:
        x+=e.end[0]
        y+=e.end[1]

    x_center = x/len(path)
    y_center = y/len(path)
    return x_center, y_center

class OverlapEnum(object):
    fully_covers = 1
    partially_overlap = 2
    fully_lays_inside = 3
    no_overlap = 4

class AABB(object):
    """Axis-Aligned Bounding Box.

    Represents a rectangle with sides parallel to the coordinate system.

    """
    def __init__(self, sx, sy, ex, ey):
        debug("AABB sx, sy, ex, ey: "+str(sx)+" "+str(sy)+" "+str(ex)+" "+str(ey))
        self.left = min(sx, ex)
        self.right = max(sx, ex)
        self.top = max(sy, ey)
        self.bottom = min(sy, ey)

    def point_in_aabb(self, pt):
        """Tests if point pt is in the bounding box.

        Returns True if the point is inside or on the boundary of the bounding
        box, False otherwise.

        """
        x = pt[0]
        y = pt[1]
        return (x>=self.left and x<=self.right and
                y>=self.bottom and y<=self.top)

    def aabb_in_aabb(self, box, check_inside_overlap=True):
        """Tests if another AABB overlaps with this one.

        Returns one of OverlapEnum's elements indicating the overlap state.

        """
        lt = self.point_in_aabb((box.left, box.top))
        lb = self.point_in_aabb((box.left, box.bottom))
        rb = self.point_in_aabb((box.right, box.bottom))
        rt = self.point_in_aabb((box.right, box.top))
            
        if lt and lb and rt and rb:
            return OverlapEnum.fully_covers
        elif (check_inside_overlap and
              box.aabb_in_aabb(self, False)==OverlapEnum.fully_covers):
            return OverlapEnum.fully_lays_inside
        elif lt or lb or rt or rb:
            return OverlapEnum.partially_overlap
        return OverlapEnum.no_overlap
        
    def __repr__(self):
        return "AABB (l: %f r: %f t: %f b: %f)" % (self.left, self.right, self.top, self.bottom)


def pt_to_pt_dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

class CircleUtils(object):
    def __init__(self, center, radius, uses_inner_space=False):
        self.center = center
        self.radius = radius
        self.uses_inner_space=uses_inner_space

    def get_aabb(self):
        """Returns the axis-aligned bounding box that encloses this circle."""
        cx = self.center[0]
        cy = self.center[1]
        r = self.radius
        return AABB(cx-r, cy-r, cx+r, cy+r)

    def distance_to_pt(self, pt):
        """Returns the distance from this circle to the given point.

        If uses_inner_space has been set to True for this circle, then any
        point inside the circle will be considered to have zero distance to
        the circle.  Otherwise, absolute distance to the edge is returned.

        """
        dist = pt_to_pt_dist(pt, self.center)-self.radius
        if self.uses_inner_space:
            return 0 if dist<0 else dist
        return abs(dist)

class PointUtils(object):
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

class ArcUtils(object):
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
        """Checks whether angle a is between the start and end of the arc."""
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
        debug("Distance to pt atan, start, end: "+str(a)+" "+str(self.sa)+" "+str(self.ea))
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
        debug("In check_if_pt_belongs")
        v = mk_vect(pt, self.center)
        if abs((self.radius) - vect_len(v))>0.001:
            debug("  radius check failed")
            return False

        a = math.atan2(pt[1]-self.center[1], pt[0]-self.center[0])
        if (self.check_angle_in_range(a)):
            debug("  radius and angle ok")
            return True
        return False

    def find_intersection(self, other_element):
        debug("In ArcUtils.find_intersection")
        oe = other_element
        if other_element.__class__.__name__ == "LineUtils":
            debug("  line to arc")
            dx = oe.end[0] - oe.start[0]
            dy = oe.end[1] - oe.start[1]
            dr = math.sqrt(dx**2 + dy**2)
            d = oe.start[0]*oe.end[1] - oe.start[1]*oe.end[0]
            desc = ((self.radius)**2)*dr**2 - d**2
            intersections = []
            if desc == 0:
                #single point
                debug("  single point")
                x_i = (d*dy+sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i = (-d*dx+abs(dy)*math.sqrt(desc))/(dr**2)
                intersections.append((x_i, y_i))
            elif desc > 0:
                #intersection
                debug("  intersection")
                x_i1 = (d*dy+sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i1 = (-d*dx+abs(dy)*math.sqrt(desc))/(dr**2)
                x_i2 = (d*dy-sign(dy)*dx*math.sqrt(desc))/(dr**2)
                y_i2 = (-d*dx-abs(dy)*math.sqrt(desc))/(dr**2)
                intersections.append((x_i1, y_i1))
                intersections.append((x_i2, y_i2))
            else:
                #no intersection
                debug("  no intersection")
                return None
            #check whether intersections are inside existing element sections
            checked_intersections = []
            for pt in intersections:
                if oe.check_if_pt_belongs(pt):
                    debug("  oe belongs")
                    if self.check_if_pt_belongs(pt):
                        debug("  self belongs")
                        checked_intersections.append(pt)
                    else:
                        debug("  self failed")
                        pass
                else:
                    debug("  oe failed")
                    pass
            if len(checked_intersections)>0:
                return checked_intersections
        else:
            debug("  Not calc util:", other_element.__class__.__name__)
        return None


class LineUtils(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_aabb(self):
        return AABB(self.start[0], self.start[1], self.end[0], self.end[1])

    # def distance_to_pt(self, pt):
    #     #dbgfname()
    #     dist = 0
    #     a = math.atan2(self.start[1]-self.end[1], self.start[0]-self.end[0])
    #     #debug("  alpha: "+str(a))
    #     sina = math.sin(a)
    #     cosa = math.cos(a)
    #     s = self.__reproject_pt(self.start, sina, cosa)
    #     #s = self.start
    #     e = self.__reproject_pt(self.end, sina, cosa)
    #     p = self.__reproject_pt(pt, sina, cosa)
    #     left = min(s[0], e[0])
    #     right = max(s[0], e[0])
    #     if p[0]<=left:
    #         dist = pt_to_pt_dist(p, (left, s[1]))
    #         return dist
    #     elif p[0]>=right:
    #         dist = pt_to_pt_dist(p, (right, s[1]))
    #         return dist
    #     a = pt_to_pt_dist(s, e) #abs(s[0]-e[0])
    #     b = pt_to_pt_dist(s, p)
    #     c = pt_to_pt_dist(e, p)
    #     p = (a+b+c)/2.0
    #     #debug("  a: "+str(a)+" b: "+str(b)+" c: "+str(c)+" p: "+str(p)+" "+str(p*(p-a)*(p-b)*(p-c)))
    #     dist = abs(math.sqrt(p*(p-a)*(p-b)*(p-c))*2/a)
    #     #debug("  dist: "+str(dist))
    #     return dist

    def distance_to_pt(self, pt):
        #dbgfname()
        s = self.start
        e = self.end
        se = mk_vect(s, e)
        l2 = vect_len2(se)
        if l2 < 0.0001:
            d = vect_len(mk_vect(s, pt))
            #debug("  distance: %f"%(d,))
            return d
        cosine = dot_product(vect_sub(pt, s), vect_sub(e, s)) / l2
        #debug("  cosine: %f"%(cosine,))
        if cosine<0.0:
            d = vect_len(mk_vect(pt, s))
            #debug("  distance: %f"%(d,))
            return d
        elif cosine>1.0:
            d = vect_len(mk_vect(pt, e))
            #debug("  distance: %f"%(d,))
            return d
        v = find_vect_normal(se)
        r = mk_vect(e, pt)
        d = abs(-v[1]*r[1]-r[0]*v[0])/vect_len(v)
        #debug("  distance: %f"%(d,))
        return d
            

    def check_if_pt_belongs(self, pt):
        x_i, y_i = pt
        minx = min(self.start[0], self.end[0])
        maxx = max(self.start[0], self.end[0])
        miny = min(self.start[1], self.end[1])
        maxy = max(self.start[1], self.end[1])

        x_intersects = False
        y_intersects = False

        if abs(minx-maxx)<0.001:
            if abs(x_i-minx)<0.001:
                x_intersects = True
            else:
                return False
        elif x_i>=minx and x_i<=maxx:
            x_intersects = True
        
        if abs(miny-maxy)<0.001:
            if abs(y_i-miny)<0.001:
                y_intersects = True
            else:
                return False
        elif y_i>=miny and y_i<=maxy:
            y_intersects = True

        if x_intersects and y_intersects:
            return True

        return False

    def find_intersection(self, other_element):
        #debug("In LineUtils.find_intersection")
        oe = other_element
        if other_element.__class__.__name__ == "LineUtils":
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
                return None
            else:
                x_i = (ob*mc-mb*oc)/det
                y_i = (ma*oc-oa*mc)/det
                if self.check_if_pt_belongs((x_i, y_i)):
                    if oe.check_if_pt_belongs((x_i, y_i)):
                        return [x_i, y_i]
                    else:
                        pass
                else:
                    pass
        elif other_element.__class__.__name__ == "ArcUtils":
            return oe.find_intersection(self)
        else:
            debug("  Not calc util:", other_element.__class__.__name__)

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
