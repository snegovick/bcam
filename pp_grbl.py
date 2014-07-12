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
