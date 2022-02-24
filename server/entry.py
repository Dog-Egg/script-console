import click
from tornado.log import enable_pretty_logging


@click.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8310, type=click.INT)
@click.option('--debug', is_flag=True)
def main(*args, **kwargs):
    enable_pretty_logging()

    import server
    server.run(*args, **kwargs)


if __name__ == '__main__':
    main()
