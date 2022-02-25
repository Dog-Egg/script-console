import functools
import json
import os
import re
import typing

import yaml
from pydantic import BaseModel, constr

import settings


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

    commands: typing.List[CommandModel] = []
    access: typing.List[AccessModel] = []
    console: ConsoleModel = ConsoleModel()


def _catch_error(method):
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

    @property
    def data(self):
        return self._data.dict()

    def read_dict(self, data: dict):
        self._data = ConfigModel(**data)

    @_catch_error
    def read_yaml(self, path: str):
        with open(path) as fp:
            data = yaml.load(fp, Loader=yaml.CLoader)
        self.read_dict(data)

    @_catch_error
    def read_json(self, path: str):
        with open(path) as fp:
            data = json.load(fp)
        self.read_dict(data)

    @property
    def commands(self):
        return self._data.commands

    @property
    def access(self):
        return self._data.access

    @property
    def console(self):
        return self._data.console

    def get_command(self, path):
        for c in self.commands:
            if re.search(c.pattern, path):
                return c


def initialize_file():
    """初始化配置文件"""
    if os.path.exists(settings.CONFIG_FILE_PATH):
        return

    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), 'template.yaml'), 'r') as tmpl:
        with open(settings.CONFIG_FILE_PATH, 'w') as fp:
            fp.write(tmpl.read())
