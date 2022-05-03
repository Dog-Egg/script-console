import os

from . import default_settings
from .typing import convert, ConvertError


class Attributes:
    def __init__(self):
        self.frozen = False  # 防止 settings 冻结前被使用，也防止 settings 冻结后被修改
        self._data = {}
        self._annotations = {}
        self._setup()

    def _setup(self):
        annotations = getattr(default_settings, '__annotations__', {})
        for name, value in vars(default_settings).items():
            if not str.isupper(name):
                continue
            if name in annotations:
                self._annotations[name] = annotations[name]
            self._data[name] = value

    def __getitem__(self, name):
        if not self.frozen:
            raise RuntimeError('not frozen before getting setting.')
        return self._data[name]

    def __setitem__(self, name, value):
        if self.frozen:
            raise RuntimeError('settings frozen.')
        if name in self._annotations:
            value = convert(value, self._annotations[name])
        self._data[name] = value


class Settings:
    def __init__(self):
        self._attributes = Attributes()
        self.from_env()

    def __getattr__(self, name):
        try:
            return self._attributes[name]
        except KeyError:
            return self.__getattribute__(name)

    def __setattr__(self, name, value):
        if str.isupper(name):
            self._attributes[name] = value
        else:
            super().__setattr__(name, value)

    def freeze(self):
        self._attributes.frozen = True

    def from_env(self):
        prefix = 'SC_'
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            try:
                self._attributes[key[len(prefix):]] = value
            except ConvertError as exc:
                raise RuntimeError('The environment variable %r, %s' % (key, exc))


settings = Settings()
