import re
import typing
from collections import namedtuple

import yaml

ScriptConf = namedtuple('ScriptConf', [
    'pattern',
    'program',
    'priority',
    'environment',
    'groups'
])


class Conf:
    def __init__(self, file):
        with open(file) as fp:
            self.data = yaml.load(fp, Loader=yaml.CLoader)
        self._script_configs = None

    def _get_script_configs(self):
        rv = []
        for item in self.data['scripts']:
            item: dict
            rv.append(ScriptConf(
                pattern=item['pattern'],
                program=item['program'],
                priority=item.get('priority', 0),
                environment=item.get('environment', {}),
                groups=item.get('groups', []),
            ))
        return rv

    @property
    def script_configs(self):
        if self._script_configs is None:
            self._script_configs = self._get_script_configs()
        return self._script_configs

    def get_script_config(self, path):
        rv: typing.Optional[ScriptConf] = None
        for c in self.script_configs:
            if re.search(c.pattern, path):
                if rv is None or c.priority > rv.priority:
                    rv = c
        return rv
