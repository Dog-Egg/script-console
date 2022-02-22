import re
import typing

import yaml
from pydantic import BaseModel


class ConfigModel(BaseModel):
    class CommandModel(BaseModel):
        pattern: str
        program: str
        environment: dict = {}

    class AccessModel(BaseModel):
        pattern: str
        groups: typing.List[str] = []

    commands: typing.List[CommandModel] = []
    access: typing.List[AccessModel] = []


class Config:
    def __init__(self, file):
        self.error = None

        try:
            with open(file) as fp:
                data = yaml.load(fp, Loader=yaml.CLoader)
            self._config = ConfigModel(**data)
        except Exception as e:
            self._config = ConfigModel()
            self.error = e

    @property
    def commands(self):
        return self._config.commands

    @property
    def access(self):
        return self._config.access

    def get_command(self, path):
        for c in self.commands:
            if re.search(c.pattern, path):
                return c
