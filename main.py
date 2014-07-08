import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ee, ep
from main_window import MainWindow
from state import state

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
        pass
        if event.button == 1:
            ep.push_event(ee.screen_left_click, (event.x, event.y))
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

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = MainWindow(width, height, Screen)
ep.mw = mw

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    mw.run()

if __name__ == "__main__":
    run()
