import os

from conf import Conf

COLOR_YELLOW = '\033[1;33m'
COLOR_RESET = '\x1B[0m'


class Runner:
    def __init__(self, conf_file):
        self.conf = Conf(conf_file)

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
