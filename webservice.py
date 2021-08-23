import json
import logging
import os
import pty
import select
import signal
import typing

import click
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging

from utils import find_scripts

SCRIPTS_DIR = os.getenv('SC_SCRIPTS_DIR') or os.path.join(os.path.dirname(__file__), 'scripts')

enable_pretty_logging()

COLOR_YELLOW = '\033[1;33m'
COLOR_RESET = '\x1B[0m'

logger = logging.getLogger(__name__)


class ScriptListApi(RequestHandler):
    def get(self):
        scripts = find_scripts(SCRIPTS_DIR)
        self.write({'scripts': scripts})


class RunScriptWs(WebSocketHandler):
    fd: typing.Optional[int]
    pid: typing.Optional[int]

    def open(self):
        script = self.get_argument('script')
        pid, fd = pty.fork()
        if pid == 0:
            print(COLOR_YELLOW + 'python %s' % script + COLOR_RESET, os.linesep)
            os.execlp('python', 'python', os.path.join(SCRIPTS_DIR, script))
        else:
            self.log('Run script %r' % script, pid)
            self.fd = fd
            self.pid = pid
            self.loop()

    def on_message(self, message):
        data = json.loads(message)
        _type, message = data['type'], data['message']
        if _type == 'message':
            writeable = select.select([], [self.fd], [], 0)[1]
            if writeable:
                if isinstance(message, str):
                    message = message.encode()
                os.write(self.fd, message)
        elif _type == 'signal':
            self.log('Client signal %s' % message)
            os.kill(self.pid, getattr(signal, message))

    def on_close(self):
        if self.pid is not None:
            self.log('Websocket closed (SIGKILL)')
            os.kill(self.pid, signal.SIGKILL)

    def send(self, message):
        if message:
            try:
                self.write_message(message)
            except WebSocketClosedError:
                pass

    def loop(self):
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        if pid != 0:
            self.log('Process finished with status %d' % status)
            self.pid, self.fd = None, None
            self.send('\nProcess finished with status %d\n' % status)
            return self.close()

        readable = select.select([self.fd], [], [], 0)[0]
        if readable:
            try:
                data = os.read(self.fd, 1024)
            except OSError:
                pass
            else:
                self.send(data)
        IOLoop.current().add_callback(self.loop)

    def log(self, message: str, pid: int = None):
        pid = self.pid if pid is None else pid
        logger.info('[PID %d] %s', pid, message)


def make_app(debug=False):
    static_path = os.path.join(os.path.dirname(__file__), 'web/build')
    app = Application([
        (r'/api/scripts', ScriptListApi),
        (r'/socket/run', RunScriptWs),
        (r'/(.*)', StaticFileHandler, dict(path=static_path, default_filename='index.html')),
    ], debug=debug)
    return app


@click.command()
@click.option('--debug', is_flag=True)
def main(debug):
    import socket
    if debug:
        port = 8300
    else:
        port = 8310
    app = make_app(debug)
    app.listen(port)

    try:
        host = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        host = 'localhost'

    print('Running on: http://%s:%d' % (host, port))
    print('Debug:', debug)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
