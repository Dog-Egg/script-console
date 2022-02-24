import logging
import os

from tornado.ioloop import IOLoop

import db
import settings
from app import make_app

logger = logging.getLogger(__name__)


def initialize_config_file():
    """初始化配置文件"""
    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    open(os.path.join(settings.SCRIPTS_DIR, settings.CONFIG_FILENAME), 'a').close()


def run(host, port, debug):
    initialize_config_file()

    app = make_app(debug)
    app.listen(port, host)

    db.init()
    logger.info('Running on: http://%s:%d', host, port)
    logger.info('Debug: %s', debug)
    IOLoop.current().start()
