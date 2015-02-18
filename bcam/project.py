from path import Path
from state import State
import state
from singleton import Singleton

from logging import debug, info, warning, error, critical
from util import dbgfname

import os
import json
from copy import deepcopy

class Step(object):
    def __init__(self, state=None, data=None):
        if data == None:
            self.state=state
        else:
            self.deserialize(data)
        self.serialized_state = self.state.serialize()

    def serialize(self):
        return {'state': self.serialized_state}

    def deserialize(self, data):
        self.state = State(data["state"])

    def __repr__(self):
        return str(self.state)


class Project(object):
    def __init__(self):
        self.steps = []

    def load(self, project_path):
        dbgfname()
        from events import ep, ee
        #global state

        debug("  loading project from "+str(project_path))
        f = open(project_path)
        data = f.read()
        f.close()
        parsed_json = json.loads(data)
        self.steps = []
        #print "json:", parsed_json
        if parsed_json["format_version"] == 2:
            step = Step(data=parsed_json["step"])
            self.steps.append(step)
            Singleton.state.set(self.steps[-1].state)
            ep.push_event(ee.update_tool_operations_list, (None))
            ep.push_event(ee.update_paths_list, (None))
            ep.mw.widget.update()
        else:
            debug("  Can't load, unsupported format")

    def push_state(self, state):
        dbgfname()
        self.steps.append(Step(state))
        depth = 50
        if (len(self.steps)>depth):
            self.steps = self.steps[-depth:]
        debug("  steps length:"+str(len(self.steps)))

    def save(self, project_path):
        if os.path.splitext(project_path)[1][1:].strip() != "bcam":
            project_path+=".bcam"

        # format 2
        f = open(project_path, 'w')
        f.write(json.dumps({'format_version': 2, 'step': self.steps[-1].serialize()}))
        f.close()
        return True

project = Project()
