import functools
import json
import os
import re
import typing

import sqlalchemy
import yaml
from pydantic import BaseModel, constr
from tornado.ioloop import IOLoop

import db


class ConfigModel(BaseModel):
    class EnvMixin(BaseModel):
        class EnvModel(BaseModel):
            name: constr(strip_whitespace=True)
            value: constr(strip_whitespace=True)

        environments: typing.List[EnvModel] = []

        @property
        def environment(self) -> dict:
            return {env.name: env.value for env in self.environments}

    class CommandModel(EnvMixin):
        pattern: str
        program: constr(strip_whitespace=True)

    class AccessModel(BaseModel):
        pattern: str
        groups: typing.List[str] = []

    class ConsoleModel(EnvMixin):
        shell: constr(strip_whitespace=True) = None

    class AuthenticationModel(BaseModel):
        allow_anonymous: bool = False

    commands: typing.List[CommandModel] = []
    access: typing.List[AccessModel] = []
    console: ConsoleModel = ConsoleModel()
    authentication: AuthenticationModel = AuthenticationModel()


def _catch_error(method) -> typing.Any:
    @functools.wraps(method)
    def decorator(self: 'Config', *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            self.error = e

    return decorator


class Config:
    def __init__(self):
        self.error = None
        self._data = ConfigModel()

    def to_dict(self):
        return self._data.dict()

    def to_json(self):
        return self._data.json()

    def read_dict(self, data: dict):
        self._data = ConfigModel(**data)

    @_catch_error
    def read_yaml(self, stream):
        self.read_dict(yaml.load(stream, Loader=yaml.CLoader))

    @_catch_error
    def read_json(self, content: str):
        self.read_dict(json.loads(content))

    @property
    def commands(self):
        return self._data.commands

    @property
    def access(self):
        return self._data.access

    @property
    def console(self):
        return self._data.console

    @property
    def authentication(self):
        return self._data.authentication

    def get_command(self, path):
        for c in self.commands:
            if re.search(c.pattern, path):
                return c

    @classmethod
    def sync_build(cls):
        instance = cls()

        async def main():
            async with db.async_session() as session:
                query: db.Config = (await session.execute(
                    sqlalchemy.select(db.Config).where(db.Config.version == 'v1'))).scalar_one_or_none()
                if query:
                    instance.read_json(query.data)
                # TODO 兼容 .sc-conf.yaml 配置内容
                else:
                    with open(os.path.join(os.path.dirname(__file__), 'template.yaml')) as fp:
                        instance.read_yaml(fp)

        IOLoop.current().run_sync(main)
        return instance
