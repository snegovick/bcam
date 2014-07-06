import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from loader_dxf import DXFLoader


class EVEnum:
    load_click = "load_click"
    load_file = "load_file"

class EventProcessor(object):
    ee = EVEnum()
    file_data = None
    event_list = []
    def __init__(self):
        self.events = {
            self.ee.load_click: self.load_click,
            self.ee.load_file: self.load_file,
        }

    def push_event(self, event, *args):
        self.event_list.append((event, args))

    def process(self):
        for e, args in self.event_list:
            if e in self.events:
                self.events[e](args)
            else:
                print "Unknown event:", e, args
        self.event_list = []

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
            #print dialog.get_filename(), 'selected'
            self.push_event(self.ee.load_file, dialog.get_filename())
        elif response == gtk.RESPONSE_CANCEL:
            pass
            #print 'Closed, no files selected'
        dialog.destroy()

    def load_file(self, args):
        print "load file", args
        dxfloader = DXFLoader()
        self.file_data = dxfloader.load(args[0])
        if self.file_data != None:
            for p in self.file_data:
                label = gtk.Label(p.name)
                list_item = gtk.ListItem()
                list_item.add(label)
                label.show()
                gtklist.add(list_item)

