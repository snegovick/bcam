from __future__ import absolute_import, division, print_function

from logging import debug, info, warning, error, critical
import logging
from bcam.util import dbgfname
from bcam import util

logging.basicConfig(level=logging.WARNING)

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from bcam.events import EVEnum, EventProcessor, ee, ep
from bcam.main_window import MainWindow
from bcam.singleton import Singleton
from bcam import project, state

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None
    expose_called = True

    def periodic(self):
        if (self.expose_called == False):
            return True
        ep.process()
        return True

    def save_project(self, *args):
        pass

    def update(self):
        self.expose_called = False
        self.queue_draw()

    def scroll_event(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            ep.push_event(ee.scroll_up, (None))
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            ep.push_event(ee.scroll_down, (None))
    
    def button_press_event(self, widget, event):
        debug("button press: "+ str(event.button))
        if event.button == 1:
            ep.push_event(ee.screen_left_press, (event.x, event.y))

    def key_press_event(self, widget, event):
        debug("key press:" + str(event.keyval))
        if event.keyval == 65307: # ESC
            ep.push_event(ee.deselect_all, (None))
        elif event.keyval == 65505: # shift
            ep.push_event(ee.shift_press, (None))
        elif event.keyval == 65507: # ctrl
            ep.push_event(ee.ctrl_press, (None))

    def key_release_event(self, widget, event):
        if event.keyval == 65505: # shift
            ep.push_event(ee.shift_release, (None))
        elif event.keyval == 65507: # shift
            ep.push_event(ee.ctrl_release, (None))

    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(ee.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        self.expose_called = True
        Singleton.state.set_screen_offset((self.allocation.width//2, self.allocation.height//2))
        
        offset = Singleton.state.get_offset()
        scale = Singleton.state.get_scale()

        cr_gdk = self.window.cairo_create()
        surface = cr_gdk.get_target()
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.allocation.width, self.allocation.height)
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.rectangle(0, 0, self.allocation.width, self.allocation.height)
        cr.fill()

        # grid drawing
        cr.set_line_width(1.0/Singleton.state.scale[0])
        #cr.set_line_width(1.0)
        cr.translate(offset[0], offset[1])
        cr.scale(Singleton.state.scale[0], -Singleton.state.scale[1])

        cr.set_source_rgb(1.0, 0, 0)
        cr.move_to(-10, 0)
        cr.line_to(10, 0)
        cr.stroke()

        cr.move_to(0, -10)
        cr.line_to(0, 10)
        cr.stroke()
        cr.identity_matrix()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        step = 1.0
        xsteps = self.allocation.width/Singleton.state.scale[0]/step
        ysteps = self.allocation.height/Singleton.state.scale[1]/step
        maxsteps = max(xsteps, ysteps)
        mins = 40
        maxs = 80
        if (maxsteps < mins):
            while (maxsteps < mins):
                if (step//10 == 0):
                    break
                step//=10
                xsteps = self.allocation.width/Singleton.state.scale[0]/step
                ysteps = self.allocation.height/Singleton.state.scale[1]/step
                maxsteps = max(xsteps, ysteps)
        if (maxsteps > maxs):
            while (maxsteps > maxs):
                step*=10
                xsteps = self.allocation.width/Singleton.state.scale[0]/step
                ysteps = self.allocation.height/Singleton.state.scale[1]/step
                maxsteps = max(xsteps, ysteps)

        x = (offset[0]/Singleton.state.scale[0])%(step)
        y = (offset[1]/Singleton.state.scale[1])%(step)
        while (x*Singleton.state.scale[0]<self.allocation.width):
            y = (offset[1]/Singleton.state.scale[1])%(step)
            while (y*Singleton.state.scale[1]<self.allocation.height):
                cr.rectangle(x*Singleton.state.scale[0], y*Singleton.state.scale[1], 1, 1)
                cr.fill()
                y += step
            x += step
        
        if Singleton.state.paths!=None:
            cr.translate(offset[0], offset[1])
            cr.scale(Singleton.state.scale[0], -Singleton.state.scale[1])
            for p in Singleton.state.paths:
                p.draw(cr)
            cr.identity_matrix()

        if Singleton.state.tool_operations!=None:
            cr.translate(offset[0], offset[1])
            cr.scale(Singleton.state.scale[0], -Singleton.state.scale[1])
            for o in Singleton.state.tool_operations:
                o.draw(cr)
            cr.identity_matrix()

        # draw selection box
        if ep.left_press_start != None:
            cr.translate(offset[0], offset[1])
            cr.scale(Singleton.state.scale[0], -Singleton.state.scale[1])
            Singleton.state.settings.select_box_lt.set_lt(cr)
            w = ep.pointer_position[0] - ep.left_press_start[0]
            h = ep.pointer_position[1] - ep.left_press_start[1]
            cr.rectangle(ep.left_press_start[0], ep.left_press_start[1], w, h)
            cr.fill()
            cr.identity_matrix()

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = None
        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    args = {"--log": {"is_set": util.NOT_SET, "has_option": util.NO_OPTION, "option": None},
            "--plugins-dir": {"is_set": util.NOT_SET, "has_option": util.HAS_OPTION, "option": None}}
    util.parse_args(args)
    if args["--log"]["is_set"]:
        logging.getLogger("").setLevel(logging.DEBUG)

    Singleton.plugins_dir = None
    if args["--plugins-dir"]["is_set"]:
        Singleton.plugins_dir = args["--plugins-dir"]["option"]

    global mw, ep
    state.State()
    mw = MainWindow(Screen)
    Singleton.mw = mw
    ep.mw = mw
    project.project.push_state(Singleton.state, "initial state")
    mw.run()

if __name__ == "__main__":
    run()
