import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys


class EVEnum:
    load_click = "load_click"

class EventProcessor(object):
    ee = EVEnum()
    def __init__(self):
        self.events = {
            self.ee.load_click: self.load_click,
        }

    def process(self, event, *args):
        if event in self.events:
            self.events[event](args)
        else:
            print "Unknown event:", event, args

    def load_click(self, args):
        dialog = gtk.FileChooserDialog("Open..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name("Blueprints")
        filter.add_mime_type("Application/dxf")
        filter.add_pattern("*.dxf")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'selected'
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            dialog.destroy()
