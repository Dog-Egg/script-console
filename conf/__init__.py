import fnmatch
import os
import re
import shlex
import typing
from collections import namedtuple
from configparser import ConfigParser

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'default.conf')

FileConf = namedtuple('FileConf', [
    'pattern',
    'program',
    'priority',
    'environment',
    'groups'
])


class Conf:
    def __init__(self, file):
        self.cfg = ConfigParser()
        self.cfg.read([DEFAULT_CONFIG_FILE, file])
        self._file_configs = None

    def _get_file_configs(self):
        file_section_pattern = re.compile('file:(.*)')
        rv = []
        for name in self.cfg.sections():
            section = self.cfg[name]
            match = file_section_pattern.match(name)
            if match:
                pattern = match.group(1)
                rv.append(FileConf(
                    pattern=pattern,
                    program=section['program'],
                    priority=section.getint('priority', 0),
                    environment=dict_of_key_value_pairs(section.get('environment', '')),
                    groups=shlex.split(section.get('groups', '')),
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
            if fnmatch.fnmatch(path, c.pattern):
                if rv is None or c.priority > rv.priority:
                    rv = c
        return rv


def dict_of_key_value_pairs(arg):
    """ parse KEY=val,KEY2=val2 into {'KEY':'val', 'KEY2':'val2'}
        Quotes can be used to allow commas in the value
    """
    lexer = shlex.shlex(str(arg))
    lexer.wordchars += '/.+-():'

    tokens = list(lexer)
    tokens_len = len(tokens)

    d = {}
    i = 0
    while i < tokens_len:
        k_eq_v = tokens[i:i + 3]
        if len(k_eq_v) != 3 or k_eq_v[1] != '=':
            raise ValueError("Unexpected end of key/value pairs in value '%s'" % arg)
        d[k_eq_v[0]] = k_eq_v[2].strip('\'"')
        i += 4
    return d
