from bcam.singleton import Singleton
from bcam.plugin import Plugin
from bcam.tool_op_offset_follow import TOOffsetFollow
from bcam.project import project
from logging import debug


import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

mass_offset_follow = "mass_offset_follow"

class MassOffsetFollow(Plugin):
    def __init__(self):
        self.expanded = False
        self.selected_elements = None

    def expand(self, args):
        if self.expanded:
            self.tool_subvbox.hide()
            self.expanded = False
        else:
            self.tool_subvbox.show()
            self.expanded = True

    def event_processor(self, args):
        if (self.selected_elements == None):
            self.selected_elements = Singleton.ep.selected_elements[:]        

        connected = Singleton.ep.join_elements(None)
        debug("  connected: "+str(connected))
        if connected != None:
            path_follow_op = TOOffsetFollow(Singleton.state, index=len(Singleton.state.tool_operations), depth=Singleton.state.get_settings().get_material().get_thickness(), offset=self.spin.get_value())
            if path_follow_op.apply(connected):
                Singleton.state.tool_operations.append(path_follow_op)
                Singleton.ep.push_event(Singleton.ee.update_tool_operations_list, (None))
                for e in connected.elements:
                    if e in self.selected_elements:
                        self.selected_elements.remove(e)
                Singleton.ep.selected_elements = self.selected_elements[:]
                for e in self.selected_elements:
                    e.set_selected()
                Singleton.mw.widget.update()
                Singleton.state.set_operation_in_progress(path_follow_op)
                Singleton.ep.push_event(Singleton.ee.update_progress, True)
                Singleton.ep.push_event(mass_offset_follow, args)
            else:
                self.selected_elements = None
                Singleton.state.unset_operation_in_progress()
                project.push_state(Singleton.state, "mass_offset_follow_click")
                Singleton.ep.deselect_all(None)
        else:
            self.selected_elements = None
            Singleton.state.unset_operation_in_progress()
            project.push_state(Singleton.state, "mass_offset_follow_click")
            Singleton.ep.deselect_all(None)

    def register(self):
        debug("Registering mass offset follow plugin")
        Singleton.ep.set_event(mass_offset_follow, [self.event_processor])
        self.tool_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.tool_subvbox = gtk.VBox(homogeneous=False, spacing=0)
        self.tool_subvbox.set_border_width(5)
        self.mass_offset_follow_expand_button = gtk.Button("Mass offset follow")
        self.mass_offset_follow_expand_button.connect("clicked", self.expand)
        
        self.mass_offset_follow_button = gtk.Button("Run")
        self.mass_offset_follow_button.connect("clicked", lambda *args: Singleton.ep.push_event(mass_offset_follow, args))

        self.tool_vbox.pack_start(self.mass_offset_follow_expand_button, expand=False, fill=False, padding=0)
        self.tool_vbox.pack_start(self.tool_subvbox, expand=False, fill=False, padding=0)

        dct = {}
        spin_hbox = Singleton.mw.gen_labeled_spin(dct, "Offset", 0)
        self.spin = dct["spin"]
        self.tool_subvbox.pack_start(spin_hbox, expand=False, fill=False, padding=0)
        self.tool_subvbox.pack_start(self.mass_offset_follow_button, expand=False, fill=False, padding=0)

        Singleton.mw.left_vbox.pack_start(self.tool_vbox, expand=False, fill=False, padding=0)
        self.tool_vbox.show()
        self.mass_offset_follow_expand_button.show()
        self.mass_offset_follow_button.show()

    def __repr__(self):
        return "Mass offset plugin"

    def __str__(self):
        return "Sets offset for multiple selected paths"

debug("Appending mass offset follow plugin")
Singleton.plugins.append(MassOffsetFollow())

