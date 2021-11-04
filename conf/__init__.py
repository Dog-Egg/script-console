import re
import typing

import yaml
import marshmallow as ma

import settings


class _CommandsSchema(ma.Schema):
    pattern = ma.fields.String(required=True)
    program = ma.fields.String(required=True)
    environment = ma.fields.Dict(missing={})


class _AccessSchema(ma.Schema):
    pattern = ma.fields.String(required=True)
    groups = ma.fields.List(ma.fields.String(), missing=[])


class _Schema(ma.Schema):
    commands = ma.fields.List(ma.fields.Nested(_CommandsSchema), missing=[])
    access = ma.fields.List(ma.fields.Nested(_AccessSchema), missing=[])


class ConfError(Exception):
    def __init__(self):
        self.args = '%r parsing failure.' % settings.CONFIG_FILENAME,


class Conf:
    def __init__(self, file):
        self.error = None

        try:
            with open(file) as fp:
                data = yaml.load(fp, Loader=yaml.CLoader)
            self.data = _Schema().load(data)
        except Exception as e:
            self.data = _Schema().load({})
            try:
                raise ConfError from e
            except ConfError as e2:
                self.error = e2

    @property
    def commands(self) -> typing.List[typing.Dict]:
        return self.data['commands']

    @property
    def access(self) -> typing.List[typing.Dict]:
        return self.data['access']

    def get_command(self, path):
        for c in self.commands:
            if re.search(c['pattern'], path):
                return c
