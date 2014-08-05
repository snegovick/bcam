import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from loader_dxf import DXFLoader
from state import state
from tool_op_drill import TODrill
from tool_op_exact_follow import TOExactFollow
from tool_op_offset_follow import TOOffsetFollow
from tool_op_pocketing import TOPocketing
from settings import settings
from calc_utils import AABB, OverlapEnum
from path import Path
from project import project

class EVEnum:
    load_click = "load_click"
    save_click = "save_click"
    load_file = "load_file"
    save_file = "save_file"
    load_project_click = "load_project_click"
    save_project_click = "save_project_click"
    load_project = "load_project"
    save_project = "save_project"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    pointer_motion = "pointer_motion"
    drill_tool_click = "drill_tool_click"
    deselect_all = "deselect_all"
    shift_press = "shift_press"
    shift_release = "shift_release"
    update_paths_list = "update_paths_lilst"
    update_tool_operations_list = "update_tool_operations_lilst"
    path_list_selection_changed = "path_list_selection_changed"
    tool_operations_list_selection_changed = "tool_operations_list_selection_changed"
    exact_follow_tool_click = "exact_follow_tool_click"
    offset_follow_tool_click = "offset_follow_tool_click"
    pocket_tool_click = "pocket_tool_click"
    update_settings = "update_settings"
    tool_operation_up_click = "tool_operation_up_click"
    tool_operation_down_click = "tool_operation_down_click"
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    hscroll = "hscroll"
    vscroll = "vscroll"
    tool_paths_check_button_click = "tool_paths_check_button_click"
    paths_check_button_click = "paths_check_button_click"
    path_delete_button_click = "path_delete_button_click"
    tool_operation_delete_button_click = "tool_operation_delete_button_click"

class EventProcessor(object):
    ee = EVEnum()
    file_data = None
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    operations = []
    left_press_start = None
    pointer_position = None
    shift_pressed = False

    def __init__(self):
        self.events = {
            self.ee.load_click: self.load_click,
            self.ee.save_click: self.save_click,
            self.ee.load_file: self.load_file,
            self.ee.save_file: self.save_file,
            self.ee.load_project_click: self.load_project_click,
            self.ee.save_project_click: self.save_project_click,
            self.ee.load_project: self.load_project,
            self.ee.save_project: self.save_project,
            self.ee.screen_left_press: self.screen_left_press,
            self.ee.screen_left_release: self.screen_left_release,
            self.ee.pointer_motion: self.pointer_motion,
            self.ee.drill_tool_click: self.drill_tool_click,
            self.ee.deselect_all: self.deselect_all,
            self.ee.shift_press: self.shift_press,
            self.ee.shift_release: self.shift_release,
            self.ee.update_paths_list: self.update_paths_list,
            self.ee.path_list_selection_changed: self.path_list_selection_changed,
            self.ee.exact_follow_tool_click: self.exact_follow_tool_click,
            self.ee.offset_follow_tool_click: self.offset_follow_tool_click,
            self.ee.pocket_tool_click: self.pocket_tool_click,
            self.ee.update_tool_operations_list: self.update_tool_operations_list,
            self.ee.tool_operations_list_selection_changed: self.tool_operations_list_selection_changed,
            self.ee.update_settings: self.update_settings,
            self.ee.tool_operation_up_click: self.tool_operation_up_click,
            self.ee.tool_operation_down_click: self.tool_operation_down_click,
            self.ee.scroll_up: self.scroll_up,
            self.ee.scroll_down: self.scroll_down,
            self.ee.hscroll: self.hscroll,
            self.ee.vscroll: self.vscroll,
            self.ee.tool_paths_check_button_click: self.tool_paths_check_button_click,
            self.ee.paths_check_button_click: self.paths_check_button_click,
            self.ee.path_delete_button_click: self.path_delete_button_click,
            self.ee.tool_operation_delete_button_click: self.tool_operation_delete_button_click,
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
        mimes = [("Blueprints (*.dxf)", "Application/dxf", "*.dxf")]
        result = self.mw.mk_file_dialog("Open ...", mimes)
        if result!=None:
            self.push_event(self.ee.load_file, result)

    def save_click(self, args):
        mimes = [("GCode (*.ngc)", "Application/dxf", "*.dxf")]
        result = self.mw.mk_file_save_dialog("Save ...", mimes)
        if result!=None:
            self.push_event(self.ee.save_file, result)

    def load_project_click(self, args):
        mimes = [("BCam projects (*.bcam)", "Application/bcam", "*.bcam")]
        result = self.mw.mk_file_dialog("Open project ...", mimes)
        if result!=None:
            self.push_event(self.ee.load_project, result)

    def save_project_click(self, args):
        mimes = [("BCam project (*.bcam)", "Application/bcam", "*.bcam")]
        result = self.mw.mk_file_save_dialog("Save project ...", mimes)
        if result!=None:
            self.push_event(self.ee.save_project, result)

    def update_paths_list(self, args):
        if self.file_data != None:
            self.mw.clear_list(self.mw.gtklist)
            for p in self.file_data:
                if p.name[0] == '*':
                    continue
                self.mw.add_item_to_list(self.mw.gtklist, p.name, self.ee.paths_check_button_click)
        project.push_state(self.file_data, self.operations, settings, state)

    def update_tool_operations_list(self, args):
        if self.operations != None:
            self.mw.clear_list(self.mw.tp_gtklist)
            for p in self.operations:
                self.mw.add_item_to_list(self.mw.tp_gtklist, p.display_name, self.ee.tool_paths_check_button_click)
        project.push_state(self.file_data, self.operations, settings, state)

    def load_file(self, args):
        print "load file", args
        dxfloader = DXFLoader()
        self.file_data = dxfloader.load(args[0])
        self.push_event(self.ee.update_paths_list, (None))

    def save_file(self, args):
        print "save file", args
        file_path = args[0]
        out = ""
        for p in self.operations:
            out+=p.get_gcode()
        f = open(file_path, "w")
        f.write(out)
        f.close()

    def load_project(self, args):
        print "load project", args
        pass

    def save_project(self, args):
        print "save project", args
        project_path = args[0]
        project.save(project_path)

    def screen_left_press(self, args):
        print "press at", args
        offset = state.get_offset()
        cx = (args[0][0]-offset[0])/state.scale[0]
        cy = (args[0][1]-offset[1])/state.scale[1]
        self.left_press_start = (cx, cy)
        self.pointer_position = (cx, cy)

    def screen_left_release(self, args):
        print "release at", args
        offset = state.get_offset()
        cx = (args[0][0]-offset[0])/state.scale[0]
        cy = (args[0][1]-offset[1])/state.scale[1]
        self.pointer_position = (cx, cy)
        if (self.left_press_start!=None):
            if self.file_data == None:
                self.left_press_start=None
                return

            # just a click
            dx = abs(cx-self.left_press_start[0])
            dy = abs(cy-self.left_press_start[1])
            print "dx, dy:", dx, dy
            if dx<1 and dy<1:
                for p in self.file_data:
                    for e in p.elements:
                        if (e.distance_to_pt((cx, cy))<1):
                            #print "accepted"
                            if self.shift_pressed:
                                if not e in self.selected_elements:
                                    e.set_selected()
                                    self.selected_elements.append(e)
                            else:
                                if e in self.selected_elements:
                                    self.selected_elements.remove(e)
                                    e.unset_selected()
                                else:
                                    self.deselect_all(None)
                                    e.set_selected()
                                    self.selected_elements.append(e)
                            
            # selection with a box
            else:
                ex = cx
                ey = cy
                sx = self.left_press_start[0]
                sy = self.left_press_start[1]
                select_aabb = AABB(sx, sy, ex, ey)
                if not self.shift_pressed:
                    self.deselect_all(None)
                for p in self.file_data:
                    for e in p.elements:
                        if not e in self.selected_elements:
                            e_aabb = e.get_aabb()
                            if (e_aabb != None):
                                print "e:", e_aabb
                                print "select:", select_aabb
                                
                                overlap = select_aabb.aabb_in_aabb(e_aabb)
                                print "overlap",overlap
                                if (overlap != OverlapEnum.no_overlap) and (overlap != OverlapEnum.fully_lays_inside):
                                    e.set_selected()
                                    self.selected_elements.append(e)
            #print self.selected_elements

        self.left_press_start=None
        
    def pointer_motion(self, args):
        offset = state.get_offset()
        cx = (args[0][0]-offset[0])/state.scale[0]
        cy = (args[0][1]-offset[1])/state.scale[1]
        self.pointer_position = (cx, cy)
        self.mw.cursor_pos_label.set_text("%.3f:%.3f"%(cx, cy))

    def drill_tool_click(self, args):
        print "drill tool click:", args
        print self.selected_elements
        for e in self.selected_elements:
            drl_op = TODrill(settings, index=len(self.operations))
            if drl_op.apply(e):
                self.operations.append(drl_op)
                self.push_event(self.ee.update_tool_operations_list, (None))
        print self.operations

    def join_elements(self, args):
        if self.selected_elements!=None:
            print self.selected_elements
            p = Path(self.selected_elements, "path", settings.get_def_lt())
            connected = p.mk_connected_path()
            if connected != None:
                connected.name = connected.name+" "+str(len(self.file_data))
                self.deselect_all(None)
                for e in connected.elements:
                    for i, p in enumerate(self.file_data):
                        if e in self.file_data[i].elements:
                            self.file_data[i].elements.remove(e)
                self.file_data.append(connected)
                self.push_event(self.ee.update_paths_list, (None))
                return connected
        return None

    def deselect_all(self, args):
        for e in self.selected_elements:
            e.toggle_selected()
        self.selected_elements = []

    def shift_press(self, args):
        self.shift_pressed = True

    def shift_release(self, args):
        self.shift_pressed = False

    def path_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        self.deselect_all(None)
        self.selected_path = None
        for li in selection:
            name = li.children()[0].children()[1].get_text()
            for p in self.file_data:
                if p.name == name:
                    self.selected_path = p
                    for e in p.elements:
                        if not e in self.selected_elements:
                            e.set_selected()
                            self.selected_elements.append(e)

    def tool_operations_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        self.selected_tool_operation = None
        for li in selection:
            name = li.children()[0].children()[1].get_text()
            for p in self.operations:
                if p.display_name == name:
                    self.selected_tool_operation = p
                    self.mw.new_settings_vbox(p.get_settings_list(), p.display_name+" settings")

    def exact_follow_tool_click(self, args):
        print "exact follow tool click:", args
        connected = self.join_elements(None)
        print "selected path:", self.selected_path
        if connected != None:
            path_follow_op = TOExactFollow(settings, index=len(self.operations))
            if path_follow_op.apply(connected):
                self.operations.append(path_follow_op)
                self.push_event(self.ee.update_tool_operations_list, (None))

    def offset_follow_tool_click(self, args):
        print "offset follow tool click:", args
        connected = self.join_elements(None)
        print "selected path:", self.selected_path
        print "connected:", connected
        if connected != None:
            path_follow_op = TOOffsetFollow(settings, index=len(self.operations))
            if path_follow_op.apply(connected):
                self.operations.append(path_follow_op)
                self.push_event(self.ee.update_tool_operations_list, (None))

    def pocket_tool_click(self, args):
        print "pocket tool click:", args
        connected = self.join_elements(None)
        print "selected path:", self.selected_path
        if connected != None:
            pocket_op = TOPocketing(settings, index=len(self.operations))
            if pocket_op.apply(connected):
                self.operations.append(pocket_op)
                self.push_event(self.ee.update_tool_operations_list, (None))


    def update_settings(self, args):
        print "settings update:", args
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)
        project.push_state(self.file_data, self.operations, settings, state)

    def tool_operation_up_click(self, args):
        print "tool operation up"
        if self.selected_tool_operation==None:
            return
        if len(self.operations)==0:
            return
        cur_idx = self.operations.index(self.selected_tool_operation)
        print "cur idx:", cur_idx
        if cur_idx == 0:
            return
        temp = self.selected_tool_operation
        self.operations.remove(self.selected_tool_operation)
        self.operations.insert(cur_idx-1, temp)
        self.push_event(self.ee.update_tool_operations_list, (None))

    def tool_operation_down_click(self, args):
        print "tool operation down"
        if self.selected_tool_operation==None:
            return
        if len(self.operations)==0:
            return
        cur_idx = self.operations.index(self.selected_tool_operation)
        print "cur idx:", cur_idx
        if cur_idx == len(self.operations)-1:
            return
        temp = self.selected_tool_operation
        self.operations.remove(self.selected_tool_operation)
        self.operations.insert(cur_idx+1, temp)
        self.push_event(self.ee.update_tool_operations_list, (None))

    def scroll_up(self, args):
        print "scroll up"
        if state.scale[0]<=1:
            state.scale = (state.scale[0]+0.1, state.scale[1]+0.1)
        else:
            state.scale = (state.scale[0]+1, state.scale[1]+1)
        #project.push_state(self.file_data, self.operations, settings, state)

    def scroll_down(self, args):
        print "scroll down"
        if state.scale[0]>0.1:
            if state.scale[0]<=1:
                state.scale = (state.scale[0]-0.1, state.scale[1]-0.1)
            else:
                state.scale = (state.scale[0]-1, state.scale[1]-1)
        #project.push_state(self.file_data, self.operations, settings, state)

    def hscroll(self, args):
        print "hscroll:", args
        print args[0][0].get_value()
        offset = state.get_base_offset()
        state.set_base_offset((-args[0][0].get_value(), offset[1]))

    def vscroll(self, args):
        print "vscroll:", args
        print args[0][0].get_value()
        offset = state.get_base_offset()
        state.set_base_offset((offset[0], -args[0][0].get_value()))

    def tool_paths_check_button_click(self, args):
        name = args[0][0]
        for o in self.operations:
            if o.display_name == name:
                o.display = not o.display
                break

    def paths_check_button_click(self, args):
        name = args[0][0]
        for p in self.file_data:
            if p.name == name:
                p.display = not p.display
                break

    def path_delete_button_click(self, args):
        if self.selected_path in self.file_data:
            self.file_data.remove(self.selected_path)
            self.selected_path = None
            self.push_event(self.ee.update_paths_list, (None))

    def tool_operation_delete_button_click(self, args):
        if self.selected_tool_operation in self.operations:
            self.operations.remove(self.selected_tool_operation)
            self.selected_tool_operation = None
            self.push_event(self.ee.update_tool_operations_list, (None))
        
ee = EVEnum()
ep = EventProcessor()
