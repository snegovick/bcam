import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ee, ep
from main_window import MainWindow
from state import state
from settings import settings

width=640
height=480

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None

    def periodic(self):
        self.queue_draw()
        ep.process()
        return True
    
    def button_press_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_press, (event.x, event.y))

    def key_press_event(self, widget, event):
        print event.keyval
        if event.keyval == 65307: # ESC
            ep.push_event(ee.deselect_all, (None))
        elif event.keyval == 65505: # shift
            ep.push_event(ee.shift_press, (None))

    def key_release_event(self, widget, event):
        if event.keyval == 65505: # shift
            ep.push_event(ee.shift_release, (None))

    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(ee.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        state.offset = (self.allocation.width/2,self.allocation.height/2)

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
                p.draw(cr, state.offset)

        if ep.operations!=None:
            cr.translate(state.offset[0], state.offset[1])
            cr.scale(state.scale[0], state.scale[1])
            for o in ep.operations:
                o.draw(cr)
            cr.identity_matrix()

        # draw selection box
        if ep.left_press_start != None:
            cr.translate(state.offset[0], state.offset[1])
            cr.scale(state.scale[0], state.scale[1])
            settings.select_box_lt.set_lt(cr)
            w = ep.pointer_position[0] - ep.left_press_start[0]
            h = ep.pointer_position[1] - ep.left_press_start[1]
            cr.rectangle(ep.left_press_start[0], ep.left_press_start[1], w, h)
            cr.fill()
            cr.identity_matrix()

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = MainWindow(width, height, Screen)
ep.mw = mw

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    mw.run()

if __name__ == "__main__":
    run()
