from postprocessor import Postprocessor

class PPGRBL:
    def __init__(self):
        pass

    def move_to(self, pt):
        out = "G01 X%.3fY%.3fZ%.3f\r\n" % (pt[0], pt[1], pt[2])
        return out

    def move_to_rapid(self, pt):
        out = "G00 X%.3fY%.3fZ%.3f\r\n" % (pt[0], pt[1], pt[2])
        return out

    def set_feedrate(self, fr):
        out = "G94\r\n"
        out+= "F%.3f\r\n" % fr
        return out

    def set_metric(self):
        return "G21\r\n"

    def set_absolute(self):
        return "G90\r\n"

    def mk_cw_arc(self, r, end):
        out = "G02 X%.3fY%.3fZ%.3f R%.3f\r\n" % (end[0], end[1], end[2], r)
        return out

    def mk_ccw_arc(self, r, end):
        out = "G03 X%.3fY%.3fZ%.3f R%.3f\r\n" % (end[0], end[1], end[2], r)
        return out

    def mk_cw_ijk_arc(self, center, end):
        out = "G02 X%.3fY%.3fZ%.3f I%.3fJ%.3fK%.3f\r\n" % (end[0], end[1], end[2], center[0], center[1], center[2])
        return out

    def mk_ccw_ijk_arc(self, center, end):
        out = "G03 X%.3fY%.3fZ%.3f I%.3fJ%.3fK%.3f\r\n" % (end[0], end[1], end[2], center[0], center[1], center[2])
        return out
