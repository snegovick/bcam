import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ee, ep

class MainWindow(object):
    def __init__(self, w, h, Widget):
        self.tool_diameter_spin = {}
        self.tool_feedrate_spin = {}
        self.tool_vert_step = {}

        self.window = gtk.Window()
        self.window.resize(w, h)
        self.window.connect("delete-event", gtk.main_quit)
        self.widget = Widget()
        self.widget.connect("button_press_event", self.widget.button_press_event)
        self.widget.connect("button_release_event", self.widget.button_release_event)
        self.widget.connect("motion_notify_event", self.widget.motion_notify_event)
        self.widget.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)

        self.__mk_left_vbox()

        self.hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.hbox.pack_start(self.left_vbox, expand=False, fill=False, padding=0)
        self.hbox.pack_start(self.widget, expand=True, fill=True, padding=0)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
        #widget.window = window
        
        #widget.paths = paths

        gobject.timeout_add(10, self.widget.periodic)
        self.window.add(self.hbox)

    def run(self):
        self.window.show_all()
        self.window.present()
        gtk.main()

    def __mk_labeled_spin(self, dct, mlabel, callback, value=3.0, lower=0, upper=999.0, step_incr=0.01, page_incr=0.5):
        hbox = gtk.HBox(homogeneous=False, spacing=0)
        dct["hbox"] = hbox
        label = gtk.Label(mlabel)
        dct["label"] = label
        spin = gtk.SpinButton(adjustment=gtk.Adjustment(value=value, lower=lower, upper=upper, step_incr=step_incr, page_incr=page_incr, page_size=0), climb_rate=0.01, digits=3)
        dct["spin"] = spin
        #alignment = gtk.Alignment(1.0, 0.0, 1.0, 0.0)
        #alignment.add(spin)
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.pack_start(spin, expand=True, fill=True, padding=0)
        return hbox

    def __mk_right_vbox(self):
        self.right_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.tool_label = gtk.Label("Tool settings")
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

        self.tool_diameter_hbox = self.__mk_labeled_spin(self.tool_diameter_spin, "Diameter, mm: ", None)
        self.right_vbox.pack_start(self.tool_diameter_hbox, expand=False, fill=False, padding=0)

        self.tool_feedrate_hbox = self.__mk_labeled_spin(self.tool_feedrate_spin, "Feedrate, mm/s: ", None)
        self.right_vbox.pack_start(self.tool_feedrate_hbox, expand=False, fill=False, padding=0)

        self.tool_vertical_step_hbox = self.__mk_labeled_spin(self.tool_vert_step, "Vertical step, mm: ", None)
        self.right_vbox.pack_start(self.tool_vertical_step_hbox, expand=False, fill=False, padding=0)


        self.tool_label = gtk.Label("Contour following settings")
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

        self.tool_label = gtk.Label("Pocketing settings")
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

    def __mk_left_vbox(self):
        self.left_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.load_dxf = gtk.Button(label="Load...")
        self.load_dxf.connect("clicked", lambda *args: ep.push_event(ee.load_click, args))
        self.left_vbox.pack_start(self.load_dxf, expand=False, fill=False, padding=0)

        self.paths_label = gtk.Label("Paths")
        self.scrolled_window = gtk.ScrolledWindow()
        self.gtklist = gtk.List()
        self.scrolled_window.add_with_viewport(self.gtklist)
        self.left_vbox.pack_start(self.paths_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.scrolled_window, expand=True, fill=True, padding=0)

        self.tool_ops_label = gtk.Label("Tool operations")
        self.drill_tool_button = gtk.Button("Drill")
        self.drill_tool_button.connect("clicked", lambda *args: ep.push_event(ee.drill_tool_click, args))
        self.left_vbox.pack_start(self.tool_ops_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.drill_tool_button, expand=False, fill=False, padding=0)

        self.tools_label = gtk.Label("Tools")
        self.mk_connected_path = gtk.Button("Join elements")
        self.mk_connected_path.connect("clicked", lambda *args: ep.push_event(ee.join_elements_click, args))
        self.left_vbox.pack_start(self.tools_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.mk_connected_path, expand=False, fill=False, padding=0)
