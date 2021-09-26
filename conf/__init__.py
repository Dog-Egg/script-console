import re
import typing
from collections import namedtuple

import yaml

FileConf = namedtuple('FileConf', [
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
        self._file_configs = None

    def _get_file_configs(self):
        rv = []
        for item in self.data['scripts']:
            item: dict
            rv.append(FileConf(
                pattern=item['pattern'],
                program=item['program'],
                priority=item.get('priority', 0),
                environment=item.get('environment', {}),
                groups=item.get('groups', []),
            ))
        return rv

    @property
    def file_configs(self):
        if self._file_configs is None:
            self._file_configs = self._get_file_configs()
        return self._file_configs

    def get_file_config(self, path):
        rv: typing.Optional[FileConf] = None
        for c in self.file_configs:
            if re.search(c.pattern, path):
                if rv is None or c.priority > rv.priority:
                    rv = c
        return rv
