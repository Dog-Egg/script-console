import logging
import os

import click
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging

import db
import settings
from app import make_app

enable_pretty_logging()

logger = logging.getLogger(__name__)


def initialize_config_file():
    """初始化配置文件"""
    os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
    open(os.path.join(settings.SCRIPTS_DIR, settings.CONFIG_FILENAME), 'a').close()


@click.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8310, type=click.INT)
@click.option('--debug', is_flag=True)
def main(host, port, debug):
    initialize_config_file()

    app = make_app(debug)
    app.listen(port, host)

    db.init()
    logger.info('Running on: http://%s:%d', host, port)
    logger.info('Debug: %s', debug)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
