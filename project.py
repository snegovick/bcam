from path import Path
from state import State
from tool_op_drill import TODrill


import json
from copy import deepcopy

class Step(object):
    def __init__(self, state=None, data=None):
        if data == None:
            self.state=state
            pass
        else:
            self.deserialize(data)

    def serialize(self):
        return {'state': self.state.serialize()}

    def deserialize(self, data):
        self.state = State(data["state"])


class Project(object):
    def __init__(self):
        self.steps = []

    def load(self, project_path):
        print "loading project from", project_path
        f = open(project_path)
        data = f.read()
        f.close()
        print "json:", parsed_json
        if parsed_json["format_version"] == 1:
            for s in parsed_json["steps"]:
                self.steps.append(Step(data=s))
            state = self.steps[-1].state
        else:
            print "Can't load, unsupported format"

    def push_state(self, state):
        self.steps.append(Step(state))

    def save(self, project_path):
        # format 1
        serialized_steps = [s.serialize() for s in self.steps]
        f = open(project_path, 'w')
        f.write(json.dumps({'format_version': 1, 'steps': serialized_steps}))
        f.close()
        return True

project = Project()
