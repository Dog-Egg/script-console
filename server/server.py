import logging

from tornado.ioloop import IOLoop

import config
import db
from app import make_app

logger = logging.getLogger(__name__)


def run(host, port, debug):
    config.initialize_file()

    app = make_app(debug)
    app.listen(port, host)

    db.init()
    logger.info('Running on: http://%s:%d', host, port)
    logger.info('Debug: %s', debug)
    IOLoop.current().start()
