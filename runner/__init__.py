import os
import traceback

from conf import Conf

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
    def __init__(self, conf_file):
        self.conf = Conf(conf_file)

    @catch_exec
    def __call__(self, path):
        conf = self.conf.get_file_config(path)
        if not conf:
            raise RuntimeError('Not found executable program')

        program = conf.program
        name = os.path.basename(program)
        env = os.environ.copy()
        env.update(conf.environment)
        print(COLOR_YELLOW + ('Command "%s"' % ' '.join([program, path])) + COLOR_RESET, os.linesep)
        os.execlpe(program, name, path, env)
