import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from loader_dxf import DXFLoader
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
        
        for p in self.paths:
            p.draw(cr, (self.allocation.width/2,self.allocation.height/2), 0.2, (0,0,0))

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

def __mk_labeled_spin(mlabel, callback, value=3.0, lower=0, upper=999.0, step_incr=0.01, page_incr=0.5):
    hbox = gtk.HBox(homogeneous=False, spacing=0)
    label = gtk.Label(mlabel)
    spin = gtk.SpinButton(adjustment=gtk.Adjustment(value=value, lower=lower, upper=upper, step_incr=step_incr, page_incr=page_incr, page_size=0), climb_rate=0.01, digits=3)
    #alignment = gtk.Alignment(1.0, 0.0, 1.0, 0.0)
    #alignment.add(spin)
    hbox.pack_start(label, expand=False, fill=False, padding=0)
    hbox.pack_start(spin, expand=True, fill=True, padding=0)
    return hbox

def __mk_right_vbox():
    right_vbox = gtk.VBox(homogeneous=False, spacing=0)

    tool_label = gtk.Label("Tool settings")
    right_vbox.pack_start(tool_label, expand=False, fill=False, padding=0)

    tool_diameter_hbox = __mk_labeled_spin("Diameter, mm: ", None)
    right_vbox.pack_start(tool_diameter_hbox, expand=False, fill=False, padding=0)

    tool_feedrate_hbox = __mk_labeled_spin("Feedrate, mm/s: ", None)
    right_vbox.pack_start(tool_feedrate_hbox, expand=False, fill=False, padding=0)

    tool_vertical_step_hbox = __mk_labeled_spin("Vertical step, mm: ", None)
    right_vbox.pack_start(tool_vertical_step_hbox, expand=False, fill=False, padding=0)


    tool_label = gtk.Label("Contour following settings")
    right_vbox.pack_start(tool_label, expand=False, fill=False, padding=0)

    tool_label = gtk.Label("Pocketing settings")
    right_vbox.pack_start(tool_label, expand=False, fill=False, padding=0)

    return right_vbox

def __mk_left_vbox():
    left_vbox = gtk.VBox(homogeneous=False, spacing=0)
    load_dxf = gtk.Button(label="Load...")
    load_dxf.connect("clicked", lambda *args: ep.process(ee.load_click, args))
    left_vbox.pack_start(load_dxf, expand=False, fill=False, padding=0)

    paths_label = gtk.Label("Paths")
    scrolled_window = gtk.ScrolledWindow()
    gtklist = gtk.List()
    scrolled_window.add_with_viewport(gtklist)
    left_vbox.pack_start(paths_label, expand=False, fill=False, padding=0)
    left_vbox.pack_start(scrolled_window, expand=True, fill=True, padding=0)

    return left_vbox
        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
    dxfloader = DXFLoader()
    #paths = dxfloader.load("./gear.dxf")
    

    window = gtk.Window()
    window.resize(width, height)
    window.connect("delete-event", gtk.main_quit)
    widget = Widget()
    widget.connect("button_press_event", widget.button_press_event)
    widget.set_events(gtk.gdk.BUTTON_PRESS_MASK)
    #widget.window = window

    #widget.paths = paths

    left_vbox = __mk_left_vbox()

    hbox = gtk.HBox(homogeneous=False, spacing=0)
    hbox.pack_start(left_vbox, expand=False, fill=False, padding=0)
    hbox.pack_start(widget, expand=True, fill=True, padding=0)

    right_vbox = __mk_right_vbox()
    hbox.pack_start(right_vbox, expand=False, fill=False, padding=0)

    gobject.timeout_add(10, widget.periodic)
    window.add(hbox)
    window.show_all()
    window.present()
    gtk.main()

if __name__ == "__main__":
    run(Screen)
