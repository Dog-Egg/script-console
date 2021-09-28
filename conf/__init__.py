import re
import typing
from collections import namedtuple

import yaml
import marshmallow as ma

import settings

ScriptConf = namedtuple('ScriptConf', [
    'pattern',
    'program',
    'priority',
    'environment',
    'groups'
])


class _DataScriptItemSchema(ma.Schema):
    pattern = ma.fields.String(required=True)
    program = ma.fields.String(required=True)
    priority = ma.fields.Integer(missing=0)
    environment = ma.fields.Dict(missing={})
    groups = ma.fields.List(ma.fields.String(), missing=[])

    class Meta:
        unknown = ma.EXCLUDE


class _DataSchema(ma.Schema):
    scripts = ma.fields.List(ma.fields.Nested(_DataScriptItemSchema), required=True)

    class Meta:
        unknown = ma.EXCLUDE


class ConfError(Exception):
    def __init__(self):
        self.args = '%r parsing failure.' % settings.CONFIG_FILENAME,


class Conf:
    def __init__(self, file):
        self.error = None

        try:
            with open(file) as fp:
                data = yaml.load(fp, Loader=yaml.CLoader)
            self.data = _DataSchema().load(data)
        except Exception as e:
            self.data = {'scripts': []}
            try:
                raise ConfError from e
            except ConfError as e2:
                self.error = e2

        self._script_configs = None

    def _get_script_configs(self):
        rv = []
        for item in self.data['scripts']:
            item: dict
            rv.append(ScriptConf(**item))
        return rv

    @property
    def script_configs(self):
        if self._script_configs is None:
            self._script_configs = self._get_script_configs()
        return self._script_configs

    def get_script_config(self, path):
        rv: typing.Optional[ScriptConf] = None
        for c in self.script_configs:
            if re.search(c.pattern, path):
                if rv is None or c.priority > rv.priority:
                    rv = c
        return rv
