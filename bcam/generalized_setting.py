class TOSTypes:
    button = "button"
    float = "float"

class TOSetting:
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
