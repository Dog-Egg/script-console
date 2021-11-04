import os

from conf import Conf

COLOR_YELLOW = '\033[1;33m'
COLOR_RESET = '\x1B[0m'


class Runner:
    def __init__(self, conf_file):
        conf = Conf(conf_file)
        if conf.error:
            raise conf.error
        self.conf = conf

    def __call__(self, path):
        command = self.conf.get_command(path)
        if not command:
            raise RuntimeError('Not found executable program')

        program = command['program']
        name = os.path.basename(program)
        env = os.environ.copy()
        env.update(command['environment'])
        print(COLOR_YELLOW + ('Command "%s"' % ' '.join([program, path])) + COLOR_RESET, os.linesep)
        os.execlpe(program, name, path, env)
