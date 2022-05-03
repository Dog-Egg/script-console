import functools
import inspect
import typing

import sqlalchemy
from tornado.web import RequestHandler, HTTPError

import db
from conf import Config
from fs import FileSystem


class APIHandler(RequestHandler):
    def __init_subclass__(cls, **kwargs):
        # 为子类已实现的请求方法添加一个验证装饰器
        for name in cls.SUPPORTED_METHODS:
            name = name.lower()
            method = getattr(cls, name, None)
            if method is None \
                    or method is cls._unimplemented_method \
                    or getattr(method, '_not_authenticate', False):
                continue
            setattr(cls, name, _authenticate(method))

    @property
    def fs(self) -> FileSystem:
        return self.settings['fs']

    @property
    def config(self) -> Config:
        return self.settings['config']

    def compute_etag(self):
        pass

    def data_received(self, chunk: bytes) -> typing.Optional[typing.Awaitable[None]]:
        pass

    async def get_current_user(self):
        token = self.get_secure_cookie('sessionid')
        if not token:
            return

        token = token.decode()
        async with db.async_session() as session:
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


def _authenticate(method):
    @functools.wraps(method)
    async def wrapper(self: APIHandler, *args, **kwargs):
        if not self.config.authentication.allow_anonymous:
            user = await self.current_user
            if not user:
                raise HTTPError(401)
        rv = method(self, *args, **kwargs)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    return wrapper


def not_authenticate(method):
    method._not_authenticate = True
    return method


def admin_required(method):
    @functools.wraps(method)
    async def wrapper(self: APIHandler, *args, **kwargs):
        user = await self.current_user
        if not user or not user.is_admin:
            raise HTTPError(403)
        rv = method(self, *args, **kwargs)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    return wrapper
