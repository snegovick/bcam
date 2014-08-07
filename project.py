import json

class Step(object):
    def __init__(self, paths, tool_operations, settings, state):
        self.paths=paths
        self.tool_operations=tool_operations
        self.settings=settings
        self.state=state

    def serialize(self):
        return {'paths': [p.serialize() for p in self.paths], "tool_operations": [to.serialize() for to in self.tool_operations], 'settings': self.settings.serialize(), 'state': self.state.serialize()}

    def deserialize(self, data):
        pass

class Project(object):
    def __init__(self):
        self.steps = []

    def load(self, project_path):
        pass

    def push_state(self, paths, operations, settings, state):
        self.steps.append(Step(paths, operations, settings, state))

    def save(self, project_path):
        # format 1
        serialized_steps = [s.serialize() for s in self.steps]
        f = open(project_path, 'w')
        f.write(json.dumps({'format_version': 1, 'steps': serialized_steps}))
        f.close()
        return True

project = Project()
