import logging

import click
from tornado.ioloop import IOLoop

import db
from conf import settings
from web import make_app
from utils import log

log.config()

logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8310, type=click.INT)
@click.option('--debug', is_flag=True)
def main(host, port, debug):
    if debug:
        settings.DEBUG = True
    settings.freeze()

    admin_token = db.init()

    app = make_app()
    app.listen(port, host)

    print('Running on: http://%s:%d' % (host, port))
    print('DEBUG:', settings.DEBUG)
    print('Admin Token:', admin_token)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
