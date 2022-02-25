import functools
import inspect
import typing

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from tornado.web import RequestHandler, HTTPError

import db
import settings
from config import Config
from fs import FileSystem


class BaseHandler(RequestHandler):
    fs = FileSystem(settings.SCRIPTS_DIR)

    def compute_etag(self):
        pass

    def data_received(self, chunk: bytes) -> typing.Optional[typing.Awaitable[None]]:
        pass

    async def get_current_user(self):
        token = self.get_secure_cookie('sessionid')
        if not token:
            return

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
        return self.finish({'message': message, 'errors': errors})

    @property
    def config(self) -> Config:
        key = '_sc_config'
        if not hasattr(self, key):
            config = Config()
            config.read_yaml(settings.CONFIG_FILE_PATH)
            setattr(self, key, config)
        return getattr(self, key)


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
