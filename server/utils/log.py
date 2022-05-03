import enum
import logging.config

from conf import settings


class Color(str, enum.Enum):
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\x1b[33;20m'


class ConsoleHandler(logging.StreamHandler):
    def __init__(self, color: Color = None):
        super().__init__()

        fmt = '[%(levelname).1s %(asctime)s %(name)s:%(lineno)d]'
        if color:
            fmt = color + fmt + '\x1b[0m'
        fmt += ' %(message)s'
        formatter = logging.Formatter(
            fmt=fmt,
            datefmt='%y%m%d %H:%M:%S'
        )
        self.setFormatter(formatter)


class RequireDebugFalse(logging.Filter):
    def filter(self, record):
        return not settings.DEBUG


class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        return settings.DEBUG


def config():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            'sqlalchemy': {
                'handlers': ['console.sqlalchemy'],
                'level': 'INFO',
                'propagate': False,
            },
            'tornado': {
                'handlers': ['console.tornado'],
                'level': 'DEBUG',
                'propagate': False,
            }
        },
        'filters': {
            'require_debug_false': {
                '()': 'utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'class': 'utils.log.ConsoleHandler',
                'color': Color.YELLOW,
            },
            'console.sqlalchemy': {
                'class': 'utils.log.ConsoleHandler',
                'color': Color.BLUE,
                'filters': ['require_debug_true'],
            },
            'console.tornado': {
                'class': 'utils.log.ConsoleHandler',
                'color': Color.GREEN,
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    })
