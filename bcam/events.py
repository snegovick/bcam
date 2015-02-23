from __future__ import absolute_import, division

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
import os

from bcam.loader_dxf import DXFLoader
from bcam.tool_operation import TOResult
from bcam.tool_op_drill import TODrill
from bcam.tool_op_exact_follow import TOExactFollow
from bcam.tool_op_offset_follow import TOOffsetFollow
from bcam.tool_op_pocketing import TOPocketing
from bcam.calc_utils import AABB, OverlapEnum
from bcam.path import Path
from bcam.project import project
from bcam.generalized_setting import TOSTypes

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

from bcam.singleton import Singleton
from bcam.state import State

class EVEnum:
    load_click = "load_click"
    save_click = "save_click"
    load_file = "load_file"
    save_file = "save_file"
    load_project_click = "load_project_click"
    save_project_click = "save_project_click"
    load_project = "load_project"
    save_project = "save_project"
    new_project_click = "new_project_click"
    quit_click = "quit_click"
    screen_left_press = "screen_left_press"
    screen_left_release = "screen_left_release"
    pointer_motion = "pointer_motion"
    drill_tool_click = "drill_tool_click"
    deselect_all = "deselect_all"
    shift_press = "shift_press"
    shift_release = "shift_release"
    ctrl_press = "ctrl_press"
    ctrl_release = "ctrl_release"
    update_paths_list = "update_paths_list"
    update_tool_operations_list = "update_tool_operations_list"
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
    update_progress = "update_progress"
    undo_click = "undo_click"
    redo_click = "redo_click"

class EventProcessor(object):
    ee = EVEnum()
    event_list = []
    selected_elements = []
    selected_path = None
    selected_tool_operation = None
    left_press_start = None
    pointer_position = None
    shift_pressed = False
    ctrl_pressed = False

    def __init__(self):
        Singleton.ee = self.ee
        Singleton.ep = self
        self.events = {
            self.ee.load_click: self.load_click,
            self.ee.save_click: self.save_click,
            self.ee.load_file: self.load_file,
            self.ee.save_file: self.save_file,
            self.ee.load_project_click: self.load_project_click,
            self.ee.save_project_click: self.save_project_click,
            self.ee.load_project: self.load_project,
            self.ee.save_project: self.save_project,
            self.ee.new_project_click: self.new_project_click,
            self.ee.quit_click: self.quit_click,
            self.ee.screen_left_press: self.screen_left_press,
            self.ee.screen_left_release: self.screen_left_release,
            self.ee.pointer_motion: self.pointer_motion,
            self.ee.drill_tool_click: self.drill_tool_click,
            self.ee.deselect_all: self.deselect_all,
            self.ee.shift_press: self.shift_press,
            self.ee.shift_release: self.shift_release,
            self.ee.ctrl_press: self.ctrl_press,
            self.ee.ctrl_release: self.ctrl_release,
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
            self.ee.update_progress: self.update_progress,
            self.ee.undo_click: self.undo_click,
            self.ee.redo_click: self.redo_click,
        }

    def reset(self):
        self.selected_elements = []
        self.selected_path = None
        self.selected_tool_operation = None
        self.left_press_start = None

    def push_event(self, event, *args):
        self.event_list.append((event, args))

    def process(self):
        event_list = self.event_list[:]
        self.event_list = []
        for e, args in event_list:
            if e in self.events:
                self.events[e](args)
            else:
                dbgfname()
                warning("  Unknown event:"+str(e)+" args: "+str(args))
                warning("  Please report")

    def load_click(self, args):
        mimes = [("Blueprints (*.dxf)", "Application/dxf", "*.dxf")]
        result = self.mw.mk_file_dialog("Open ...", mimes)
        if result!=None:
            self.push_event(self.ee.load_file, result)

    def save_click(self, args):
        mimes = [("GCode (*.ngc)", "Application/ngc", "*.ngc")]
        result = self.mw.mk_file_save_dialog("Save ...", mimes)
        if result!=None:
            self.push_event(self.ee.save_file, result)

    def load_project_click(self, args):
        mimes = [("BCam projects (*.bcam)", "Application/bcam", "*.bcam")]
        result = self.mw.mk_file_dialog("Open project ...", mimes)
        if result!=None:
            self.push_event(self.ee.load_project, result)

    def save_project_click(self, args):
        dbgfname()
        debug("  save project clicked")
        mimes = [("BCam project (*.bcam)", "Application/bcam", "*.bcam")]
        result = self.mw.mk_file_save_dialog("Save project ...", mimes)
        if result!=None:
            self.save_project((result, ))

    def new_project_click(self, args):
        dbgfname()
        debug("  new project clicked")
        if not Singleton.state.is_clean():
            debug("  not clean, ask to save")
            if self.mw.mk_question_dialog("Current project has some unsaved data.\nWould you like to save it?"):
                self.save_project_click(None)

        self.reset()
        Singleton.state = State()
        self.push_event(self.ee.update_tool_operations_list, (None))
        self.push_event(self.ee.update_paths_list, (None))
        project.push_state(Singleton.state, "new_project_click")
        self.mw.widget.update()

    def quit_click(self, args):
        dbgfname()
        debug("  quit clicked")
        if not Singleton.state.is_clean():
            debug("  not clean, ask to save")
            if self.mw.mk_question_dialog("Current project has some unsaved data.\nWould you like to save it?"):
                self.save_project_click(None)
            exit(0)
        else:
            exit(0)

    def update_paths_list(self, args):
        if Singleton.state.paths != None:
            self.mw.clear_list(self.mw.gtklist)
            for p in Singleton.state.paths:
                if p.name[0] == '*':
                    continue
                self.mw.add_item_to_list(self.mw.gtklist, p.name, self.ee.paths_check_button_click)

    def update_tool_operations_list(self, args):
        if Singleton.state.tool_operations != None:
            self.mw.clear_list(self.mw.tp_gtklist)
            for p in Singleton.state.tool_operations:
                self.mw.add_item_to_list(self.mw.tp_gtklist, p.display_name, self.ee.tool_paths_check_button_click)

    def load_file(self, args):
        dbgfname()
        debug("  load file: "+str(args))
        dxfloader = DXFLoader()
        Singleton.state.add_paths(dxfloader.load(args[0]))
        self.push_event(self.ee.update_paths_list, (None))
        project.push_state(Singleton.state, "load_file")
        self.mw.widget.update()
        feedrate = Singleton.state.settings.tool.get_feedrate()
        debug("  feedrate: "+str(feedrate))

    def save_file(self, args):
        dbgfname()
        debug("  save file: "+str(args))
        file_path = args[0]
        if os.path.splitext(file_path)[1][1:].strip() != "ngc":
            file_path+=".ngc"
        out = ""
        out+=Singleton.state.settings.default_pp.set_metric()
        out+=Singleton.state.settings.default_pp.set_absolute()
        feedrate = Singleton.state.settings.tool.get_feedrate()
        debug("  feedrate: "+str(feedrate))
        out+=Singleton.state.settings.default_pp.set_feedrate(feedrate)
        out+= Singleton.state.settings.default_pp.move_to_rapid([0, 0, Singleton.state.settings.tool.default_height])
        for p in Singleton.state.tool_operations:
            out+=p.get_gcode()
        out+= Singleton.state.settings.default_pp.move_to_rapid([0, 0, Singleton.state.settings.tool.default_height])
        f = open(file_path, "w")
        f.write(out)
        f.close()

    def load_project(self, args):
        dbgfname()
        debug("  load project: "+str(args))
        project_path = args[0]
        project.load(project_path)
        self.mw.update_right_vbox()

    def save_project(self, args):
        dbgfname()
        debug("  save project: "+str(args))
        project_path = args[0]
        project.save(project_path)

    def screen_left_press(self, args):
        dbgfname()
        debug("  press at:"+str(args))
        offset = Singleton.state.get_offset()
        scale = Singleton.state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        self.left_press_start = (cx, cy)
        self.pointer_position = (cx, cy)
        self.mw.widget.update()

    def screen_left_release(self, args):
        dbgfname()
        debug("  release at: "+str(args))
        offset = Singleton.state.get_offset()
        scale = Singleton.state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        self.pointer_position = (cx, cy)
        if (self.left_press_start!=None):
            if Singleton.state.paths == None:
                self.left_press_start=None
                return

            # just a click
            dx = abs(cx-self.left_press_start[0])
            dy = abs(cy-self.left_press_start[1])
            debug("  dx, dy: "+str(dx)+" "+str(dy))
            if dx<1 and dy<1:
                for p in Singleton.state.paths:
                    for e in p.elements:
                        if (e.distance_to_pt((cx, cy))<1):
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
                for p in Singleton.state.paths:
                    for e in p.elements:
                        if not e in self.selected_elements:
                            e_aabb = e.get_aabb()
                            if (e_aabb != None):
                                debug("  e: "+str(e_aabb))
                                debug("  select:"+str(select_aabb))
                                
                                overlap = select_aabb.aabb_in_aabb(e_aabb)
                                debug("  overlap:"+str(overlap))
                                if (overlap != OverlapEnum.no_overlap) and (overlap != OverlapEnum.fully_lays_inside):
                                    e.set_selected()
                                    self.selected_elements.append(e)
        self.mw.widget.update()
        self.left_press_start=None
        
    def pointer_motion(self, args):
        offset = Singleton.state.get_offset()
        scale = Singleton.state.get_scale()
        cx = (args[0][0]-offset[0])/scale[0]
        cy = (args[0][1]-offset[1])/scale[1]
        self.pointer_position = (cx, cy)
        self.mw.cursor_pos_label.set_text("cur: %.3f:%.3f"%(cx, cy))
        self.mw.widget.update()

    def drill_tool_click(self, args):
        dbgfname()
        debug("  drill tool click:"+str(args))
        debug("  "+str(self.selected_elements))
        for e in self.selected_elements:
            debug("  thickness:"+str(Singleton.state.get_settings().get_material().get_thickness()))
            drl_op = TODrill(Singleton.state, index=len(Singleton.state.tool_operations))
            if drl_op.apply(e, Singleton.state.get_settings().get_material().get_thickness()):
                Singleton.state.tool_operations.append(drl_op)
                self.push_event(self.ee.update_tool_operations_list, (None))
                project.push_state(Singleton.state, "drill_tool_click")
        debug("  "+str(Singleton.state.tool_operations))
        self.mw.widget.update()

    def join_elements(self, args):
        dbgfname()
        sp = Singleton.state.paths
        if self.selected_elements!=None:
            debug("  selected: "+str(self.selected_elements))
            p = Path(Singleton.state, self.selected_elements, "path", Singleton.state.settings.get_def_lt().name)
            connected = p.mk_connected_path()
            debug("  connected elements: "+str(connected))
            if connected != None:
                connected.name = connected.name+" "+str(len(sp))
                self.deselect_all(None)
                for e in connected.elements:
                    for i, p in enumerate(sp):
                        if e in sp[i].elements:
                            sp[i].elements.remove(e)
                sp.append(connected)
                self.push_event(self.ee.update_paths_list, (None))
                #project.push_state(Singleton.state, "join_elements")
                return connected
        return None

    def deselect_all(self, args):
        for e in self.selected_elements:
            e.toggle_selected()
        self.selected_elements = []
        self.mw.widget.update()

    def shift_press(self, args):
        self.shift_pressed = True

    def shift_release(self, args):
        self.shift_pressed = False

    def ctrl_press(self, args):
        self.ctrl_pressed = True

    def ctrl_release(self, args):
        self.ctrl_pressed = False

    def path_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        self.deselect_all(None)
        self.selected_path = None
        for li in selection:
            name = li.children()[0].children()[1].get_text()
            for p in Singleton.state.paths:
                if p.name == name:
                    self.selected_path = p
                    for e in p.elements:
                        if not e in self.selected_elements:
                            e.set_selected()
                            self.selected_elements.append(e)
        self.mw.widget.update()

    def tool_operations_list_selection_changed(self, args):
        selection = args[0][0].get_selection()
        self.selected_tool_operation = None
        for li in selection:
            name = li.children()[0].children()[1].get_text()
            for p in Singleton.state.tool_operations:
                if p.display_name == name:
                    self.selected_tool_operation = p
                    self.mw.new_settings_vbox(p.get_settings_list(), p.display_name+" settings")
        self.mw.widget.update()

    def exact_follow_tool_click(self, args):
        dbgfname()
        debug("  exact follow tool click: "+str(args))
        connected = self.join_elements(None)
        debug("  selected path: "+str(self.selected_path))
        if connected != None:
            path_follow_op = TOExactFollow(Singleton.state, index=len(Singleton.state.tool_operations), depth=Singleton.state.get_settings().get_material().get_thickness())
            if path_follow_op.apply(connected):
                Singleton.state.add_tool_operations([path_follow_op])
                self.push_event(self.ee.update_tool_operations_list, (None))
                project.push_state(Singleton.state, "exact_follow_tool_click")
        self.mw.widget.update()

    def offset_follow_tool_click(self, args):
        dbgfname()
        debug("  offset follow tool click: "+str(args))
        connected = self.join_elements(None)
        debug("  selected path: "+str(self.selected_path))
        debug("  connected: "+str(connected))
        if connected != None:
            path_follow_op = TOOffsetFollow(Singleton.state, index=len(Singleton.state.tool_operations), depth=Singleton.state.get_settings().get_material().get_thickness())
            if path_follow_op.apply(connected):
                Singleton.state.tool_operations.append(path_follow_op)
                self.push_event(self.ee.update_tool_operations_list, (None))
                project.push_state(Singleton.state, "offset_follow_tool_click")
        self.mw.widget.update()

    def pocket_tool_click(self, args):
        #dbgfname()
        #debug("  args: "+str(args))
        if args[0] != None:
            #debug("  pocket tool click: "+str(args))
            connected = self.join_elements(None)
            #debug("  selected path: "+str(self.selected_path))
            if connected != None:
                pocket_op = TOPocketing(Singleton.state, index=len(Singleton.state.tool_operations), depth=Singleton.state.get_settings().get_material().get_thickness())
                result = pocket_op.apply(connected)
                if result == TOResult.ok:
                    if Singleton.state.get_tool_operation_by_name(pocket_op.display_name) == None:
                        Singleton.state.tool_operations.append(pocket_op)
                        project.push_state(Singleton.state, "pocket_tool_click")
                        self.push_event(self.ee.update_tool_operations_list, (None))
                elif result == TOResult.repeat:
                    Singleton.state.set_operation_in_progress(pocket_op)
                    self.push_event(self.ee.update_progress, True)
                    self.push_event(self.ee.pocket_tool_click, None)
        else:
            op = Singleton.state.get_operation_in_progress()
            #debug("  Operation in progress: "+str(op))
            if op != None:
                if op.apply(None) == TOResult.repeat:
                    self.push_event(self.ee.update_progress, True)
                    self.push_event(self.ee.pocket_tool_click, None)
                else:
                    if Singleton.state.get_tool_operation_by_name(op.display_name) == None:
                        Singleton.state.tool_operations.append(op)
                        project.push_state(Singleton.state, "pocket_tool_click")
                        self.push_event(self.ee.update_tool_operations_list, (None))
                    self.push_event(self.ee.update_progress, False)
                    Singleton.state.unset_operation_in_progress()
        self.mw.widget.update()

    def update_progress(self, args):
        if args[0] == True:
            Singleton.state.spinner_frame+=1
            Singleton.state.spinner_frame %= (len(Singleton.state.spinner)*20)
            self.mw.progress_label.set_text("progress: "+Singleton.state.spinner[int(Singleton.state.spinner_frame//20)])
            self.mw.widget.update()
        else:
            self.mw.progress_label.set_text("No task running")
            self.mw.widget.update()

    def update_settings(self, args):
        dbgfname()
        debug("  settings update: "+str(args))
        setting = args[0][0]
        if setting.type == TOSTypes.float:
            new_value = args[0][1][0].get_value()
            setting.set_value(new_value)
            project.push_state(Singleton.state, "update_settings")
        elif setting.type == TOSTypes.button:
            setting.set_value(None)
        else:
            warning("  Unknown setting type: %s"%(setting.type,))
        self.mw.widget.update()

    def tool_operation_up_click(self, args):
        dbgfname()
        debug("  tool operation up")
        if self.selected_tool_operation==None:
            return
        if len(Singleton.state.tool_operations)==0:
            return
        cur_idx = Singleton.state.tool_operations.index(self.selected_tool_operation)
        debug("  cur idx: "+str(cur_idx))
        if cur_idx == 0:
            return
        temp = self.selected_tool_operation
        Singleton.state.tool_operations.remove(self.selected_tool_operation)
        Singleton.state.tool_operations.insert(cur_idx-1, temp)
        self.push_event(self.ee.update_tool_operations_list, (None))
        project.push_state(Singleton.state, "tool_operation_up_click")

    def tool_operation_down_click(self, args):
        dbgfname()
        debug("  tool operation down")
        if self.selected_tool_operation==None:
            return
        if len(Singleton.state.tool_operations)==0:
            return
        cur_idx = Singleton.state.tool_operations.index(self.selected_tool_operation)
        debug("  cur idx: "+str(cur_idx))
        if cur_idx == len(Singleton.state.tool_operations)-1:
            return
        temp = self.selected_tool_operation
        Singleton.state.tool_operations.remove(self.selected_tool_operation)
        Singleton.state.tool_operations.insert(cur_idx+1, temp)
        self.push_event(self.ee.update_tool_operations_list, (None))
        project.push_state(Singleton.state, "tool_operation_down_click")

    def scroll_up(self, args):
        dbgfname()
        debug("  scroll up")
        if self.shift_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_vscroll.set_value(-(offset[1]+10*Singleton.state.scale[0]))
        elif self.ctrl_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_hscroll.set_value(-(offset[0]+10*Singleton.state.scale[0]))
        else:
            if Singleton.state.scale[0]<=1:
                Singleton.state.scale = (Singleton.state.scale[0]+0.1, Singleton.state.scale[1]+0.1)
            else:
                Singleton.state.scale = (Singleton.state.scale[0]+1, Singleton.state.scale[1]+1)
            #project.push_state(self.file_data, self.operations, settings, state)
        self.mw.widget.update()

    def scroll_down(self, args):
        dbgfname()
        debug("  scroll down")
        if self.shift_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_vscroll.set_value(-(offset[1]-10*Singleton.state.scale[0]))
        elif self.ctrl_pressed:
            offset = Singleton.state.get_base_offset()
            Singleton.mw.widget_hscroll.set_value(-(offset[0]-10*Singleton.state.scale[0]))
        else:
            if Singleton.state.scale[0]>0.1:
                if Singleton.state.scale[0]<=1:
                    Singleton.state.scale = (Singleton.state.scale[0]-0.1, Singleton.state.scale[1]-0.1)
                else:
                    Singleton.state.scale = (Singleton.state.scale[0]-1, Singleton.state.scale[1]-1)
            #project.push_state(self.file_data, self.operations, settings, state)
        self.mw.widget.update()

    def hscroll(self, args):
        dbgfname()
        debug("  hscroll: "+str(args))
        debug("  "+str(args[0][0].get_value()))
        offset = Singleton.state.get_base_offset()
        Singleton.state.set_base_offset((-args[0][0].get_value(), offset[1]))
        self.mw.widget.update()

    def vscroll(self, args):
        dbgfname()
        debug("  vscroll: "+str(args))
        debug("  "+str(args[0][0].get_value()))
        offset = Singleton.state.get_base_offset()
        Singleton.state.set_base_offset((offset[0], -args[0][0].get_value()))
        self.mw.widget.update()

    def tool_paths_check_button_click(self, args):
        name = args[0][0]
        for o in Singleton.state.tool_operations:
            if o.display_name == name:
                o.display = not o.display
                break
        self.mw.widget.update()

    def paths_check_button_click(self, args):
        name = args[0][0]
        for p in Singleton.state.paths:
            if p.name == name:
                p.display = not p.display
                break
        self.mw.widget.update()

    def path_delete_button_click(self, args):
        if self.selected_path in Singleton.state.paths:
            Singleton.state.paths.remove(self.selected_path)
            self.selected_path = None
            self.push_event(self.ee.update_paths_list, (None))
            project.push_state(Singleton.state, "path_delete_button_click")
        self.mw.widget.update()

    def tool_operation_delete_button_click(self, args):
        if self.selected_tool_operation in Singleton.state.tool_operations:
            Singleton.state.tool_operations.remove(self.selected_tool_operation)
            self.selected_tool_operation = None
            self.push_event(self.ee.update_tool_operations_list, (None))
            project.push_state(Singleton.state, "tool_operation_delete_button_click")
        self.mw.widget.update()

    def undo_click(self, args):
        dbgfname()
        debug("  steps("+str(len(project.steps))+") before: "+str(project.steps))
        project.step_back()
        debug("  steps("+str(len(project.steps))+") after: "+str(project.steps))
        
        self.push_event(self.ee.update_tool_operations_list, (None))
        self.push_event(self.ee.update_paths_list, (None))
        self.mw.widget.update()

    def redo_click(self, args):
        dbgfname()
        debug("  steps("+str(len(project.steps))+") before: "+str(project.steps))
        project.step_forward()
        debug("  steps("+str(len(project.steps))+") after: "+str(project.steps))
        
        self.push_event(self.ee.update_tool_operations_list, (None))
        self.push_event(self.ee.update_paths_list, (None))
        self.mw.widget.update()

ee = EVEnum()
ep = EventProcessor()
