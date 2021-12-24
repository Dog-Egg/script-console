import json
import logging
import os
import pty
import select
import signal
import traceback
import typing

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from app.base import BaseHandler

logger = logging.getLogger(__name__)


class RunScriptHandler(WebSocketHandler, BaseHandler):
    fd: typing.Optional[int]
    pid: typing.Optional[int]

    async def open(self):
        script = self.get_argument('script')
        fs = await self.get_file_system()
        pid, fd = pty.fork()
        if pid == 0:
            try:
                fs.run_file(script)
            finally:
                traceback.print_exc()
                exit(1)
        else:
            self.pid = pid
            self.fd = fd
            self.log('Run script %r' % script)
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
            return self.close(reason='finish')

        readable = select.select([self.fd], [], [], 0)[0]
        if readable:
            try:
                data = os.read(self.fd, 1024)
            except OSError:
                pass
            else:
                self.send(data)
        IOLoop.current().add_callback(self.loop)

    def log(self, message):
        logger.info('[PID %d] %s', self.pid, message)
