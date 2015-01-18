from logging import debug, info, warning, error, critical
from util import dbgfname

class Postprocessor:
    def __init__(self):
        pass

    def mk_cw_arc(self, r, end):
        dbgfname()
        debug("  mk_cw_arc is not implemented")
        return None

    def mk_ccw_arc(self, r, end):
        dbgfname()
        debug("  mk_ccw_arc is not implemented")
        return None

    def mk_line(self, start, end):
        dbgfname()
        debug("  mk_line is not implemented")
        return None

    def set_depth(self, depth):
        dbgfname()
        debug("  set_depth is not implemented")
        return None

    def move_to(self, pt):
        dbgfname()
        debug("  move_to is not implemented")
        return None

    def move_home(self):
        dbgfname()
        debug("  move_home is not implemented")
        return None

    def set_feedrate(self, fr):
        dbgfname()
        debug("  set_feedrate is not implemented")
        return None

    def set_metric(self):
        dbgfname()
        debug("  set_metric is not implemented")
        return None

    def set_imperial(self):
        dbgfname()
        debug("  set_imperial is not implemented")
        return None

    def set_absolute(self):
        dbgfname()
        debug("  set_absolute is not implemented")
        return None        

    def move_to_rapid(self):
        dbgfname()
        debug("  move_to_rapid is not implemented")
        return None
