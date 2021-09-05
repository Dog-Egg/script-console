import fnmatch
import os
import configparser
import re
import shlex
import traceback

_DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'default.conf')

COLOR_YELLOW = '\033[1;33m'
COLOR_RESET = '\x1B[0m'


def catch_exec(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            traceback.print_exc()
            exit(1)

    return wrapper


class Runner:
    def __init__(self, file=''):
        cfg = configparser.ConfigParser()
        cfg.read([_DEFAULT_CONFIG_FILE, file])
        self.cfg = cfg

    @catch_exec
    def __call__(self, path):
        section = self._get_cfg_section(path)
        if not section:
            raise RuntimeError('Not found executable program')

        program = section.get('program')
        name = os.path.basename(program)
        env = os.environ.copy()
        env.update(dict_of_key_value_pairs(section.get('environment', '')))
        print(COLOR_YELLOW + ('Command "%s"' % ' '.join([program, path])) + COLOR_RESET, os.linesep)
        os.execlpe(program, name, path, env)

    def _get_cfg_section(self, file):
        section = None
        file_section_pattern = re.compile('file:(.*)')
        for name in self.cfg.sections():
            _section = self.cfg[name]
            _section.setdefault('priority', '0')
            match = file_section_pattern.match(name)
            if match:
                pattern = match.group(1)
                if fnmatch.fnmatch(file, pattern):
                    if section is None or _section.getint('priority') > section.getint('priority'):
                        section = _section
        return section


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
