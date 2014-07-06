import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor

width=640
height=480
ee = EVEnum()
ep = EventProcessor()

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None
    paths = []

    def periodic(self):
        self.queue_draw()
        ep.process()
        return True
    
    def button_press_event(self, widget, event):
        pass
        # if event.button == 1:
        #     layer0 = objects2d[0]
        #     layer1 = objects2d[1]
        #     for obj in layer0+layer1:
        #         if obj.check_if_point_belongs(event.x - width/2., event.y-height/2.):
        #             if self.active_object != None:
        #                 self.active_object.selected = False
        #             self.active_object = obj
        #             self.active_object.selected = True
        #             obj.click_handler(event)
        #             return
        # elif event.button == 3:
        #     if self.active_object!=None:
        #         self.active_object.click_handler(event)
        #     else:
        #         print "Select object"

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context

        cr_gdk = self.window.cairo_create()
        surface = cr_gdk.get_target()
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.allocation.width, self.allocation.height)
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0, 0, self.allocation.width, self.allocation.height)
        cr.fill()
        
        if ep.file_data!=None:
            for p in ep.file_data:
                p.draw(cr, (self.allocation.width/2,self.allocation.height/2), 0.2, (0,0,0))

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

class MainWindow(object):
    def __init__(self):
        self.tool_diameter_spin = {}
        self.tool_feedrate_spin = {}
        self.tool_vert_step = {}

        self.__mk_left_vbox()

        self.hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.hbox.pack_start(self.left_vbox, expand=False, fill=False, padding=0)
        self.hbox.pack_start(self.widget, expand=True, fill=True, padding=0)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
        self.window = gtk.Window()
        self.window.resize(width, height)
        self.window.connect("delete-event", gtk.main_quit)
        self.widget = Widget()
        self.widget.connect("button_press_event", self.widget.button_press_event)
        self.widget.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        #widget.window = window
        
        #widget.paths = paths

        gobject.timeout_add(10, self.widget.periodic)
        self.window.add(self.hbox)
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
        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
    m = MainWindow()

if __name__ == "__main__":
    run(Screen)
