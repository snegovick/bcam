#-*- encoding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ee, ep
from state import state

class MainWindow(object):
    def __init__(self, w, h, Widget):
        self.tool_diameter_spin = {}
        self.tool_feedrate_spin = {}
        self.tool_vert_step = {}

        self.window = gtk.Window()
        self.window.resize(w, h)
        self.window.connect("delete-event", gtk.main_quit)

        self.menu_bar = gtk.MenuBar()
        self.file_menu = gtk.Menu()
        self.file_item = gtk.MenuItem("File")
        self.file_item.set_submenu(self.file_menu)
        self.menu_bar.append(self.file_item)

        self.new_project_item = gtk.MenuItem("New project")
        self.open_project_item = gtk.MenuItem("Open project ...")
        self.save_project_item = gtk.MenuItem("Save project ...")
        sep = gtk.SeparatorMenuItem()
        self.export_item = gtk.MenuItem("Import ...")
        self.import_item = gtk.MenuItem("Export ...")


        self.file_menu.append(self.new_project_item)
        self.file_menu.append(self.open_project_item)
        self.file_menu.append(self.save_project_item)
        self.file_menu.append(sep)
        self.file_menu.append(self.import_item)
        self.file_menu.append(self.export_item)

        self.import_item.connect("activate", lambda *args: ep.push_event(ee.load_click, args))
        self.export_item.connect("activate", lambda *args: ep.push_event(ee.save_click, args))
        self.new_project_item.connect("activate", lambda *args: ep.push_event(ee.new_project_click, args))
        self.open_project_item.connect("activate", lambda *args: ep.push_event(ee.load_project_click, args))
        self.save_project_item.connect("activate", lambda *args: ep.push_event(ee.save_project_click, args))

        self.window_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.window_vbox.pack_start(self.menu_bar, expand=False, fill=False, padding=0)
        self.window.add(self.window_vbox)

        self.widget = Widget()
        self.widget.connect("button_press_event", self.widget.button_press_event)
        self.widget.connect("button_release_event", self.widget.button_release_event)
        self.widget.connect("motion_notify_event", self.widget.motion_notify_event)
        self.widget.connect("scroll_event", self.widget.scroll_event)
        self.window.connect("key_press_event", self.widget.key_press_event)
        self.window.connect("key_release_event", self.widget.key_release_event)
        self.window.set_events(gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK)
        self.widget.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)

        self.__mk_left_vbox()

        self.hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.hbox.pack_start(self.left_vbox, expand=False, fill=False, padding=0)

        self.widget_hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.widget_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.widget_hscroll = gtk.HScrollbar(gtk.Adjustment(0.0, -1000.0, 1000.0, 0.1, 1.0, 1.0))
        self.widget_hscroll.connect("value-changed", lambda *args: ep.push_event(ee.hscroll, (args)))
        self.widget_vscroll = gtk.VScrollbar(gtk.Adjustment(0.0, -1000.0, 1000.0, 0.1, 1.0, 1.0))
        self.widget_vscroll.connect("value-changed", lambda *args: ep.push_event(ee.vscroll, (args)))
        self.widget_hbox.pack_start(self.widget, expand=True, fill=True, padding=0)
        self.widget_hbox.pack_start(self.widget_vscroll, expand=False, fill=False, padding=0)
        self.widget_vbox.pack_start(self.widget_hbox, expand=True, fill=True)
        self.widget_vbox.pack_start(self.widget_hscroll, expand=False, fill=False, padding=0)
        self.hbox.pack_start(self.widget_vbox, expand=True, fill=True, padding=0)

        self.cursor_pos_label = gtk.Label("")
        self.widget_vbox.pack_start(self.cursor_pos_label, expand=False, fill=False)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
        gobject.timeout_add(10, self.widget.periodic)
        self.window_vbox.pack_start(self.hbox, expand=True, fill=True, padding=0)

    def run(self):
        self.window.show_all()
        self.window.present()
        gtk.main()

    def new_settings_vbox(self, settings_lst, label):
        for c in self.settings_vb.children():
            self.settings_vb.remove(c)
        if settings_lst == None:
            return
        l = gtk.Label(label)
        self.settings_vb.pack_start(l, expand=False, fill=False, padding=0)
        l.show()
        print settings_lst
        for s in settings_lst:
            dct = {}
            if s.type == "float":
                w = self.__mk_labeled_spin(dct, s.display_name, s, None, s.default, s.min, s.max)
                self.settings_vb.pack_start(w, expand=False, fill=False, padding=0)

    def mk_file_dialog(self, name, mimes):
        ret = None
        dialog = gtk.FileChooserDialog(name,
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        for m in mimes:
            filter = gtk.FileFilter()
            filter.set_name(m[0])
            filter.add_mime_type(m[1])
            filter.add_pattern(m[2])
            dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            ret = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return ret

    def mk_file_save_dialog(self, name, mimes):
        ret = None
        dialog = gtk.FileChooserDialog(name,
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        for m in mimes:
            filter = gtk.FileFilter()
            filter.set_name(m[0])
            filter.add_mime_type(m[1])
            filter.add_pattern(m[2])
            dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            ret = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return ret
                
    def clear_list(self, lst):
        children = lst.children()
        for c in children:
            lst.remove(c)

    def add_item_to_list(self, lst, label_text, event):
        check_button = gtk.CheckButton("")
        check_button.set_active(True)
        check_button.unset_flags(gtk.CAN_FOCUS)
        check_button.show()
        check_button.connect("clicked", lambda *args: ep.push_event(event, (label_text, args)))

        label = gtk.Label(label_text)
        label.show()

        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.pack_start(check_button, expand=False, fill=False, padding=0)
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.show()

        list_item = gtk.ListItem()
        list_item.show()
        list_item.add(hbox)
        lst.add(list_item)

    def __mk_labeled_spin(self, dct, mlabel, data=None, callback=None, value=3.0, lower=-999.0, upper=999.0, step_incr=0.01, page_incr=0.5):
        if lower == None:
            lower = -999.0
        if upper == None:
            upper = 999.0
        if step_incr == None:
            step_incr = 0.01
        if page_incr == None:
            page_incr = 0.5
        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.show()
        dct["hbox"] = hbox
        label = gtk.Label(mlabel)
        label.show()
        dct["label"] = label
        spin = gtk.SpinButton(adjustment=gtk.Adjustment(value=value, lower=lower, upper=upper, step_incr=step_incr, page_incr=page_incr, page_size=0), climb_rate=0.01, digits=3)
        spin.connect("value-changed", lambda *args: ep.push_event(ee.update_settings, (data, args)))
        spin.show()
        dct["spin"] = spin
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.pack_start(spin, expand=True, fill=True, padding=0)
        return hbox

    def __mk_right_vbox(self):
        self.right_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.tool_label = gtk.Label("Tool settings")
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

        settings_lst = state.settings.tool.get_settings_list()
        if settings_lst != None:
            print settings_lst
            for s in settings_lst:
                dct = {}
                if s.type == "float":
                    w = self.__mk_labeled_spin(dct, s.display_name, s, None, s.default, s.min, s.max)
                    self.right_vbox.pack_start(w, expand=False, fill=False, padding=0)


        self.material_label = gtk.Label("Material settings")
        self.right_vbox.pack_start(self.material_label, expand=False, fill=False, padding=0)
        settings_lst = state.settings.material.get_settings_list()
        if settings_lst != None:
            print settings_lst
            for s in settings_lst:
                dct = {}
                if s.type == "float":
                    w = self.__mk_labeled_spin(dct, s.display_name, s, None, s.default, s.min, s.max)
                    self.right_vbox.pack_start(w, expand=False, fill=False, padding=0)

        self.settings_vb = gtk.VBox(homogeneous=False, spacing=0)
        self.right_vbox.pack_start(self.settings_vb, expand=False, fill=False, padding=0)

    def __mk_left_vbox(self):
        self.left_vbox = gtk.VBox(homogeneous=False, spacing=0)
        self.paths_label = gtk.Label("Paths")
        self.scrolled_window = gtk.ScrolledWindow()
        self.gtklist = gtk.List()
        self.gtklist.connect("selection_changed", lambda *args: ep.push_event(ee.path_list_selection_changed, args))
        self.scrolled_window.add_with_viewport(self.gtklist)
        self.left_vbox.pack_start(self.paths_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.scrolled_window, expand=True, fill=True, padding=0)
        self.path_delete_button = gtk.Button("Delete path")
        self.path_delete_button.connect("clicked", lambda *args: ep.push_event(ee.path_delete_button_click, None))
        self.left_vbox.pack_start(self.path_delete_button, expand=False, fill=False, padding=0)

        self.tool_paths_label = gtk.Label("Tool paths")
        self.tp_scrolled_window = gtk.ScrolledWindow()
        self.tp_gtklist = gtk.List()
        self.tp_gtklist.connect("selection_changed", lambda *args: ep.push_event(ee.tool_operations_list_selection_changed, args))
        self.tp_scrolled_window.add_with_viewport(self.tp_gtklist)
        self.tp_updown_hbox = gtk.HBox(homogeneous=False, spacing=0)
        self.tp_up_button = gtk.Button(u"▲")
        self.tp_down_button = gtk.Button(u"▼")
        self.tp_up_button.connect("clicked", lambda *args: ep.push_event(ee.tool_operation_up_click, args))
        self.tp_down_button.connect("clicked", lambda *args: ep.push_event(ee.tool_operation_down_click, args))
        self.tp_updown_hbox.pack_start(self.tp_up_button, expand=True, fill=True, padding=0)
        self.tp_updown_hbox.pack_start(self.tp_down_button, expand=True, fill=True, padding=0)
        self.left_vbox.pack_start(self.tool_paths_label, expand=False, fill=False, padding=0)
        self.left_vbox.pack_start(self.tp_scrolled_window, expand=True, fill=True, padding=0)
        self.left_vbox.pack_start(self.tp_updown_hbox, expand=False, fill=False, padding=0)
        self.tool_operation_delete_button = gtk.Button("Delete tool path")
        self.tool_operation_delete_button.connect("clicked", lambda *args: ep.push_event(ee.tool_operation_delete_button_click, None))
        self.left_vbox.pack_start(self.tool_operation_delete_button, expand=False, fill=False, padding=0)

        self.tool_ops_label = gtk.Label("Tool operations")
        self.left_vbox.pack_start(self.tool_ops_label, expand=False, fill=False, padding=0)

        self.drill_tool_button = gtk.Button("Drill")
        self.drill_tool_button.connect("clicked", lambda *args: ep.push_event(ee.drill_tool_click, args))
        self.left_vbox.pack_start(self.drill_tool_button, expand=False, fill=False, padding=0)

        self.exact_follow_tool_button = gtk.Button("Exact follow")
        self.exact_follow_tool_button.connect("clicked", lambda *args: ep.push_event(ee.exact_follow_tool_click, args))
        self.left_vbox.pack_start(self.exact_follow_tool_button, expand=False, fill=False, padding=0)

        self.offset_follow_tool_button = gtk.Button("Offset follow")
        self.offset_follow_tool_button.connect("clicked", lambda *args: ep.push_event(ee.offset_follow_tool_click, args))
        self.left_vbox.pack_start(self.offset_follow_tool_button, expand=False, fill=False, padding=0)

        self.pocket_tool_button = gtk.Button("Pocket")
        self.pocket_tool_button.connect("clicked", lambda *args: ep.push_event(ee.pocket_tool_click, args))
        self.left_vbox.pack_start(self.pocket_tool_button, expand=False, fill=False, padding=0)





