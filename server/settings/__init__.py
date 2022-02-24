import logging

from .default_settings import *

logger = logging.getLogger(__name__)


def _overwrite():
    """通过环境变量覆盖已有设置"""
    import os
    import importlib

    module = importlib.import_module(__name__)
    settings = {}
    for k, v in vars(module).items():
        if not k.isupper():
            continue

        name = 'SC_%s' % k
        value = os.getenv(name)
        if value:
            v = value

        setattr(module, k, v)
        settings[k] = v

    logger.info('Settings: %s', settings)


_overwrite()
