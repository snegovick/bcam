from __future__ import absolute_import, division, print_function

from bcam.path import Path
from bcam.state import State
from bcam import state
from bcam.singleton import Singleton

from logging import debug, info, warning, error, critical
from bcam.util import dbgfname

import os
import json
from copy import deepcopy

class Step(object):
    def __init__(self, state=None, data=None):
        self.dsc = ""
        if data == None:
            self.state=state
        else:
            self.deserialize(data)
        self.serialized_state = self.state.serialize()

    def unserialize(self):
        # because we cant rely on self.state, but we can rely on self.serialized_state
        self.deserialize(self.serialize())

    def serialize(self):
        return {'state': self.serialized_state}

    def deserialize(self, data):
        self.state = State(data["state"])

    def __repr__(self):
        return "<Step dsc:"+str(self.dsc)+">"#str(self.state)

class Project(object):
    def __init__(self):
        self.steps = []
        self.step_index = -1
        self.path = None

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def load(self, project_path):
        dbgfname()
        from bcam.events import ep, ee
        #global state

        self.path = project_path

        debug("  loading project from "+str(project_path))
        f = open(project_path)
        data = f.read()
        f.close()
        parsed_json = json.loads(data)
        self.steps = []
        if parsed_json["format_version"] == 2:
            step = Step(data=parsed_json["step"])
            self.steps.append(step)
            Singleton.state.set(self.steps[-1].state)
            ep.push_event(ee.update_tool_operations_list, (None))
            ep.push_event(ee.update_paths_list, (None))
            ep.mw.widget.update()
        else:
            debug("  Can't load, unsupported format")

    def save(self, project_path):
        if os.path.splitext(project_path)[1][1:].strip() != "bcam":
            project_path+=".bcam"

        # format 2
        f = open(project_path, 'w')
        f.write(json.dumps({'format_version': 2, 'step': self.steps[-1].serialize()}, indent=2))
        f.close()
        self.set_path(project_path)
        return True

    def push_state(self, state, description):
        dbgfname()
        if (self.step_index != -1):
            self.steps = self.steps[:self.step_index + 1]
            self.step_index = -1
        self.steps.append(Step(state))
        self.steps[-1].dsc = description
        depth = 50
        if (len(self.steps)>depth):
            self.steps = self.steps[-depth:]
        debug("  steps length:"+str(len(self.steps)))

    def step_back(self):
        dbgfname()
        if abs(self.step_index)<len(self.steps):
            self.step_index -= 1
            s = self.steps[self.step_index]
            s.unserialize()
            Singleton.state.set(s.state);

    def step_forward(self):
        dbgfname()
        if self.step_index < -1:
            self.step_index += 1
            s = self.steps[self.step_index]
            s.unserialize()
            Singleton.state.set(s.state);


project = Project()
