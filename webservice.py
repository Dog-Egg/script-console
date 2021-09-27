import functools
import json
import logging
import os
import pty
import select
import signal
import traceback
import typing
import inspect

import click
from tornado.web import Application, RequestHandler, StaticFileHandler, HTTPError
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

import db
from runner import Runner
from utils import find_scripts, gen_token
from settings import SCRIPTS_DIR, CONFIG_FILE_PATH

enable_pretty_logging()

logger = logging.getLogger(__name__)


def admin_required(fn):
    @functools.wraps(fn)
    async def wrapper(self: BaseHandler, *args, **kwargs):
        user = await self.current_user
        if not user or not user.is_admin:
            raise HTTPError(403)
        rv = fn(self, *args, **kwargs)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    return wrapper


class BaseHandler(RequestHandler):
    async def get_current_user(self):
        token = self.get_secure_cookie('sessionid')
        if token:
            token = token.decode()
            async with AsyncSession(db.engine) as session:
                result = await session.execute(sqlalchemy.select(db.User).where(db.User.token == token))
                user = result.scalar_one_or_none()
                return user

    @property
    async def current_user(self) -> typing.Optional[db.User]:
        key = '_current_user'
        if not hasattr(self, key):
            setattr(self, key, await self.get_current_user())
        return getattr(self, key)

    def finish_error(self, *, message=None, errors=None, status_code=400):
        self.set_status(status_code)
        self.finish({'message': message, 'errors': errors})


class FileApi(BaseHandler):
    @staticmethod
    def _get_full_path(path):
        return os.path.join(SCRIPTS_DIR, path)

    @staticmethod
    def _get_file_type(path):
        ext = os.path.splitext(path)[1]
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.yaml': 'yaml',
        }.get(ext)

    @admin_required
    def get(self):
        path = self.get_argument('path')
        full_path = self._get_full_path(path)
        try:
            with open(full_path) as fp:
                content = fp.read()
        except FileNotFoundError:
            content = None
        self.finish({"path": path, 'content': content, 'filetype': self._get_file_type(path)})

    @admin_required
    def put(self):
        path = self.get_argument('path')
        content = self.get_body_argument('content')
        full_path = self._get_full_path(path)
        with open(full_path, 'w') as fp:
            fp.write(content)
        self.finish()


class UsersApi(BaseHandler):
    @admin_required
    async def get(self):
        async with db.engine.connect() as conn:
            result = await conn.execute(sqlalchemy.select(db.User))
            users = [dict(i) for i in result.fetchall()]
            self.write(dict(users=users))

    @admin_required
    async def post(self):
        real_name = self.get_body_argument('real_name')
        group = self.get_body_argument('group', default=None) or None
        async with AsyncSession(db.engine) as session:
            data = dict(real_name=real_name, token=gen_token(), group=group)
            await session.execute(sqlalchemy.insert(db.User).values(**data))
            await session.commit()
        await self.finish(data)


class UserApi(BaseHandler):
    @admin_required
    async def delete(self, uid):
        async with AsyncSession(db.engine) as session:
            await session.execute(sqlalchemy.delete(db.User).where(db.User.id == uid))
            await session.commit()
        await self.finish()


class SignApi(BaseHandler):
    async def post(self):
        token = self.get_body_argument('token')
        async with AsyncSession(db.engine) as session:
            result = await session.execute(sqlalchemy.select(db.User).where(db.User.token == token))
            user = result.scalar_one_or_none()
        if user:
            self.set_secure_cookie('sessionid', user.token)
        else:
            self.finish_error(errors={'token': '无效的令牌'})

    def delete(self):
        self.clear_cookie('sessionid')


class MeApi(BaseHandler):
    async def get(self):
        user = await self.current_user
        if user:
            data = dict(anonymous=False, id=user.id, realName=user.real_name, group=user.group)
        else:
            data = dict(anonymous=True)
        await self.finish(data)


class ScriptListApi(BaseHandler):
    async def get(self):
        user = await self.current_user
        scripts = find_scripts(user and user.group)
        self.write({'scripts': scripts})


class RunScriptWs(WebSocketHandler):
    fd: typing.Optional[int]
    pid: typing.Optional[int]

    def open(self):
        script = self.get_argument('script')
        pid, fd = pty.fork()
        if pid == 0:
            try:
                run = Runner(CONFIG_FILE_PATH)
                run(os.path.join(SCRIPTS_DIR, script))
            finally:
                traceback.print_exc()
                exit(1)
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
    settings = {
        'debug': debug,
        'cookie_secret': '__secret__'
    }
    app = Application([
        (r'/api/scripts', ScriptListApi),
        (r'/api/users', UsersApi),
        (r'/api/users/(.*)', UserApi),
        (r'/api/me', MeApi),
        (r'/api/sign', SignApi),
        (r'/api/file', FileApi),
        (r'/socket/run', RunScriptWs),
        (r'/(.*)', StaticFileHandler, dict(path=static_path, default_filename='index.html')),
    ], **settings)
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

    db.init()
    logger.info('Running on: http://%s:%d', host, port)
    logger.info('Debug: %s', debug)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
