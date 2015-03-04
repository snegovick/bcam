from __future__ import absolute_import, division, print_function

class TOSTypes(object):
    button = "button"
    float = "float"

class TOSetting(object):
    def __init__(self, type, min=None, max=None, default=None, display_name="", parent_cb=None):
        self.type = type
        self.min = min
        self.max = max
        self.default = default
        self.display_name = display_name
        self.new_value = None
        self.parent_callback = parent_cb

    def set_value(self, v):
        self.new_value = v
        self.parent_callback(self)
