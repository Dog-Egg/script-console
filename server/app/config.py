import json
import traceback

import pydantic
import yaml
from tornado.web import HTTPError

import config
import settings
from .base import BaseHandler, admin_required


class ConfigHandler(BaseHandler):
    CONFIG_PATH = settings.CONFIG_FILE_PATH

    @admin_required
    def get(self):
        self._finish()

    def _finish(self):
        error = self.config.error
        if isinstance(self.config.error, Exception):
            error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        self.finish({'data': self.config.data, 'error': error})

    @admin_required
    def put(self):
        error = HTTPError(400)
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            raise error

        if not isinstance(data, dict):
            raise error

        try:
            model = config.ConfigModel(**data)
        except pydantic.ValidationError:
            raise error

        with open(settings.CONFIG_FILE_PATH, 'w') as fp:
            yaml.dump(model.dict(), stream=fp, Dumper=yaml.CDumper)
        self._finish()
