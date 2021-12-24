import logging

import click
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging

import db
from app import make_app

enable_pretty_logging()

logger = logging.getLogger(__name__)


@click.command()
@click.option('--debug', is_flag=True)
def main(debug):
    import socket
    port = 8310
    app = make_app(debug)
    app.listen(port)

    try:
        host = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        host = 'localhost'

    db.init()
    logger.info('Running on: http://%s:%d', host, port)
    logger.info('Debug: %s', debug)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
