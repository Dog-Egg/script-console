import datetime
import json
import logging
import os
import pty
import select
import signal
import traceback

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from app.base import BaseHandler
from fs import FileSystem

logger = logging.getLogger(__name__)


class PtyHandler(WebSocketHandler):
    pid: int
    fd: int
    subprocess_finished: bool

    def initialize(self):
        self.subprocess_finished = False

    def subprocess(self):
        raise NotImplementedError

    async def open(self):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            self.subprocess()
        else:
            self.log('Process start (%s)' % self.__class__.__name__)
            self.loop()

    def on_message(self, message):
        data = json.loads(message)
        t, message = data['type'], data['message']
        if t == 'message':
            writeable = select.select([], [self.fd], [], 0)[1]
            if writeable:
                if isinstance(message, str):
                    message = message.encode()
                os.write(self.fd, message)
        elif t == 'signal':
            self.log('Client signal %s' % message)
            os.kill(self.pid, getattr(signal, message))

    def on_close(self):
        if not self.subprocess_finished:
            self.log('Websocket closed (SIGKILL)')
            os.kill(self.pid, signal.SIGKILL)

    def send(self, message):
        try:
            self.write_message(message)
        except WebSocketClosedError:
            pass

    def loop(self):
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        if pid != 0:
            self.subprocess_finished = True
            self.log('Process finished with status %d' % status)
            self.send('\nProcess finished with status %d\n' % status)
            return self.close(reason='finish')

        readable = select.select([self.fd], [], [], 0)[0]
        if readable:
            try:
                data = os.read(self.fd, 1024)
            except OSError:
                pass
            else:
                self.send(data)
        IOLoop.current().add_timeout(datetime.timedelta(seconds=0.05), self.loop)

    def log(self, message):
        logger.info('[PID %d] %s', self.pid, message)


class RunScriptHandler(PtyHandler, BaseHandler):
    script: str
    fs: FileSystem

    async def prepare(self):
        self.script = self.get_argument('script')
        self.fs = await self.get_file_system()

    def subprocess(self):
        try:
            self.fs.run_file(self.script)
        finally:
            traceback.print_exc()
            exit(1)


class ConsoleHandler(PtyHandler):
    def subprocess(self):
        env = dict(
            TERM='xterm',
            PATH=os.environ.get('PATH', ''),
            LANG="en_US.UTF-8"
        )
        os.execlpe('bash', 'bash', env)
