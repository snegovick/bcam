#-*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from bcam.events import EVEnum, EventProcessor, ee, ep
from bcam.singleton import Singleton
from bcam.generalized_setting import TOSTypes

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname


class MainWindow(object):
    def __init__(self, Widget):
        self.tool_diameter_spin = {}
        self.tool_feedrate_spin = {}
        self.tool_vert_step = {}

        self.window = gtk.Window()
        self.window.maximize()
        self.window.connect("delete-event", gtk.main_quit)

        self.menu_bar = gtk.MenuBar()
        agr = gtk.AccelGroup()
        self.window.add_accel_group(agr)
        self.mk_file_menu(agr)
        self.mk_edit_menu(agr)

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

        self.status_hbox = gtk.HBox(homogeneous=False, spacing=5)
        self.widget_vbox.pack_start(self.status_hbox, expand=False, fill=False)

        self.cursor_pos_label = gtk.Label("")
        self.status_hbox.pack_start(self.cursor_pos_label, expand=False, fill=False)

        self.progress_label = gtk.Label("")
        self.status_hbox.pack_start(self.progress_label, expand=False, fill=False)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
        gobject.timeout_add(10, self.widget.periodic)
        self.window_vbox.pack_start(self.hbox, expand=True, fill=True, padding=0)

    def mk_file_menu(self, agr):
        self.file_menu = gtk.Menu()
        self.file_item = gtk.MenuItem("_File")
        self.file_item.set_submenu(self.file_menu)
        self.menu_bar.append(self.file_item)

        self.new_project_item = gtk.MenuItem("New project")
        key, mod = gtk.accelerator_parse("<Control>N")
        self.new_project_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        self.open_project_item = gtk.MenuItem("Open project ...")
        key, mod = gtk.accelerator_parse("<Control>O")
        self.open_project_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        self.save_project_item = gtk.MenuItem("Save project")
        key, mod = gtk.accelerator_parse("<Control>S")
        self.save_project_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        self.save_project_as_item = gtk.MenuItem("Save project as ...")
        key, mod = gtk.accelerator_parse("<Control><Shift>S")
        self.save_project_as_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        sep_export_import = gtk.SeparatorMenuItem()
        self.export_item = gtk.MenuItem("Export ...")
        self.import_item = gtk.MenuItem("Import ...")
        sep_quit = gtk.SeparatorMenuItem()
        self.quit_item = gtk.MenuItem("Quit")
        key, mod = gtk.accelerator_parse("<Control>Q")
        self.quit_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        self.file_menu.append(self.new_project_item)
        self.file_menu.append(self.open_project_item)
        self.file_menu.append(self.save_project_item)
        self.file_menu.append(self.save_project_as_item)
        self.file_menu.append(sep_export_import)
        self.file_menu.append(self.import_item)
        self.file_menu.append(self.export_item)
        self.file_menu.append(sep_quit)
        self.file_menu.append(self.quit_item)

        self.import_item.connect("activate", lambda *args: ep.push_event(ee.load_click, args))
        self.export_item.connect("activate", lambda *args: ep.push_event(ee.save_click, args))
        self.new_project_item.connect("activate", lambda *args: ep.push_event(ee.new_project_click, args))
        self.open_project_item.connect("activate", lambda *args: ep.push_event(ee.load_project_click, args))
        self.save_project_item.connect("activate", lambda *args: ep.push_event(ee.save_project_click, args))
        self.save_project_as_item.connect("activate", lambda *args: ep.push_event(ee.save_project_as_click, args))
        self.quit_item.connect("activate", lambda *args: ep.push_event(ee.quit_click, args))

    def mk_edit_menu(self, agr):
        self.edit_menu = gtk.Menu()
        self.edit_item = gtk.MenuItem("_Edit")
        self.edit_item.set_submenu(self.edit_menu)
        self.menu_bar.append(self.edit_item)

        self.undo_item = gtk.MenuItem("Undo")
        key, mod = gtk.accelerator_parse("<Control>Z")
        self.undo_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        self.redo_item = gtk.MenuItem("Redo")
        key, mod = gtk.accelerator_parse("<Control>Y")
        self.redo_item.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)

        sep_undo_redo = gtk.SeparatorMenuItem()

        self.edit_menu.append(sep_undo_redo)
        self.edit_menu.append(self.undo_item)
        self.edit_menu.append(self.redo_item)

        self.undo_item.connect("activate", lambda *args: ep.push_event(ee.undo_click, args))
        self.redo_item.connect("activate", lambda *args: ep.push_event(ee.redo_click, args))

    def run(self):
        self.window.show_all()
        self.window.present()
        gtk.main()

    def new_settings_vbox(self, settings_lst, label):
        dbgfname()
        for c in self.settings_vb.children():
            self.settings_vb.remove(c)
        if settings_lst == None:
            return
        l = gtk.Label(label)
        self.settings_vb.pack_start(l, expand=False, fill=False, padding=0)
        l.show()
        self.populate_box_with_settings(self.settings_vb, settings_lst)

    def mk_question_dialog(self, question):
        md = gtk.Dialog(title=question, parent=self.window, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        yes_button = md.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
        no_button = md.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
        yes_button.grab_default()
        vbox = md.get_content_area()
        l = gtk.Label(question)
        l.show()
        vbox.pack_end(l)
        response = md.run()
        ret = True
        if response == gtk.RESPONSE_NO:
            ret = False
        md.destroy()
        return ret

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

    def set_item_selected(self, lst, idx):
        dbgfname()
        if len(lst.children()) > idx:
            debug("  selecting %i"%(idx,))
            lst.select_child(lst.children()[idx])
        else:
            debug("  len(lst.children()) = %i, idx = %i"%(len(lst.children()), idx))

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

    def gen_labeled_spin(self, dct, mlabel, value=3.0, lower=-999.0, upper=999.0, step_incr=0.01, page_incr=0.5):
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
        spin.show()
        dct["spin"] = spin
        hbox.pack_start(label, expand=False, fill=False, padding=0)
        hbox.pack_start(spin, expand=True, fill=True, padding=0)
        return hbox

    def __mk_labeled_spin(self, dct, mlabel, data=None, value=3.0, lower=-999.0, upper=999.0, step_incr=0.01, page_incr=0.5):
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

    def __mk_button(self, dct, mlabel, data=None):
        hbox = gtk.HBox(homogeneous=False, spacing=0)
        hbox.show()
        dct["hbox"] = hbox
        button = gtk.Button(label=mlabel)
        button.connect("clicked", lambda *args: ep.push_event(ee.update_settings, (data, args)))
        button.show()
        dct["button"] = button
        hbox.pack_start(button, expand=True, fill=True, padding=0)
        return hbox

    def populate_box_with_settings(self, box, settings_lst):
        if settings_lst != None:
            debug("  "+str(settings_lst))
            for s in settings_lst:
                dct = {}
                if s.type == TOSTypes.float:
                    w = self.__mk_labeled_spin(dct, s.display_name, s, s.default, s.min, s.max)
                elif s.type == TOSTypes.button:
                    w = self.__mk_button(dct, s.display_name, s)
                else:
                    warning("  Bad tool setting: %s"%(s.type,))
                    continue
                box.pack_start(w, expand=False, fill=False, padding=0)


    def update_right_vbox(self):
        self.hbox.remove(self.hbox.children()[-1])
        children = self.right_vbox.children()
        for c in children:
            self.right_vbox.remove(c)

        self.__mk_right_vbox()
        self.hbox.pack_start(self.right_vbox, expand=False, fill=False, padding=0)
    def __mk_right_vbox(self):
        dbgfname()
        self.right_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.tool_label = gtk.Label("Tool settings")
        self.tool_label.show()
        self.right_vbox.pack_start(self.tool_label, expand=False, fill=False, padding=0)

        settings_lst = Singleton.state.get_tool().get_settings_list()
        self.populate_box_with_settings(self.right_vbox, settings_lst)


        self.material_label = gtk.Label("Material settings")
        self.material_label.show()
        self.right_vbox.pack_start(self.material_label, expand=False, fill=False, padding=0)
        settings_lst = Singleton.state.settings.material.get_settings_list()
        self.populate_box_with_settings(self.right_vbox, settings_lst)

        self.settings_vb = gtk.VBox(homogeneous=False, spacing=0)
        self.settings_vb.show()
        self.right_vbox.pack_start(self.settings_vb, expand=False, fill=False, padding=0)
        self.right_vbox.show()

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
