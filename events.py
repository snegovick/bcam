import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys

from loader_dxf import DXFLoader
from state import state
from tool_op_drill import TODrill
from tool_op_exact_follow import TOExactFollow
from settings import settings
from calc_utils import AABB, OverlapEnum
from path import Path

class EVEnum:
    load_click = "load_click"
    load_file = "load_file"
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
    update_settings = "update_settings"
    tool_operation_up_click = "tool_operation_up_click"
    tool_operation_down_click = "tool_operation_down_click"
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"

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
            self.ee.load_file: self.load_file,
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
            self.ee.update_tool_operations_list: self.update_tool_operations_list,
            self.ee.tool_operations_list_selection_changed: self.tool_operations_list_selection_changed,
            self.ee.update_settings: self.update_settings,
            self.ee.tool_operation_up_click: self.tool_operation_up_click,
            self.ee.tool_operation_down_click: self.tool_operation_down_click,
            self.ee.scroll_up: self.scroll_up,
            self.ee.scroll_down: self.scroll_down,
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

    def update_paths_list(self, args):
        if self.file_data != None:
            self.mw.clear_list(self.mw.gtklist)
            for p in self.file_data:
                if p.name[0] == '*':
                    continue
                self.mw.add_item_to_list(self.mw.gtklist, p.name)


    def update_tool_operations_list(self, args):
        if self.operations != None:
            self.mw.clear_list(self.mw.tp_gtklist)
            for p in self.operations:
                self.mw.add_item_to_list(self.mw.tp_gtklist, p.display_name)

    def load_file(self, args):
        print "load file", args
        dxfloader = DXFLoader()
        self.file_data = dxfloader.load(args[0])
        self.push_event(self.ee.update_paths_list, (None))

    def screen_left_press(self, args):
        print "press at", args
        cx = (args[0][0]-state.offset[0])/state.scale[0]
        cy = (args[0][1]-state.offset[1])/state.scale[1]
        self.left_press_start = (cx, cy)
        self.pointer_position = (cx, cy)

    def screen_left_release(self, args):
        print "release at", args
        cx = (args[0][0]-state.offset[0])/state.scale[0]
        cy = (args[0][1]-state.offset[1])/state.scale[1]
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
        cx = (args[0][0]-state.offset[0])/state.scale[0]
        cy = (args[0][1]-state.offset[1])/state.scale[1]
        self.pointer_position = (cx, cy)

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
            name = li.children()[0].get_text()
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
            name = li.children()[0].get_text()
            for p in self.operations:
                if p.display_name == name:
                    self.selected_tool_operation = p
                    self.mw.new_settings_vbox(p.get_settings_list(), p.display_name+" settings")

    def exact_follow_tool_click(self, args):
        print "exact follow tool click:", args
        connected = self.join_elements(None)
        self.selected_path = connected
        print "selected path:", self.selected_path
        if self.selected_path != None:
            path_follow_op = TOExactFollow(settings, index=len(self.operations))
            if path_follow_op.apply(self.selected_path):
                self.operations.append(path_follow_op)
                self.push_event(self.ee.update_tool_operations_list, (None))

    def update_settings(self, args):
        print "settings update:", args
        new_value = args[0][1][0].get_value()
        setting = args[0][0]
        setting.set_value(new_value)

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

        if self.operations != None:
            self.mw.clear_list(self.mw.tp_gtklist)
            for p in self.operations:
                self.mw.add_item_to_list(self.mw.tp_gtklist, p.display_name)

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

        if self.operations != None:
            self.mw.clear_list(self.mw.tp_gtklist)
            for p in self.operations:
                self.mw.add_item_to_list(self.mw.tp_gtklist, p.display_name)

    def scroll_up(self, args):
        print "scroll up"
        if state.scale[0]<=1:
            state.scale = (state.scale[0]+0.1, state.scale[1]+0.1)
        else:
            state.scale = (state.scale[0]+1, state.scale[1]+1)


    def scroll_down(self, args):
        print "scroll down"
        if state.scale[0]>0.1:
            if state.scale[0]<=1:
                state.scale = (state.scale[0]-0.1, state.scale[1]-0.1)
            else:
                state.scale = (state.scale[0]-1, state.scale[1]-1)
        
ee = EVEnum()
ep = EventProcessor()
