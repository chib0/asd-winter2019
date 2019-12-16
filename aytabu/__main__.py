#flake8
import os
import sys
import traceback
import pathlib
import click
import datetime

from unittest.mock import Mock

from . import upload_thought
from . import run_server
from . import run_webserver


class Log:

    def __init__(self):
        self.quiet = False
        self.traceback = False

    def __call__(self, message):
        if self.quiet:
            return
        if self.traceback and sys.exc_info(): # there's an active exception
            message += os.linesep + traceback.format_exc().strip()
        click.echo(message)


log = Log()


@click.group()
@click.option('-q', '--quiet', is_flag=True)
@click.option('-t', '--traceback', is_flag=True)
def main(quiet=False, traceback=False):
    log.quiet = quiet
    log.traceback = traceback


@main.group()
@click.pass_context
def thought(context):
    pass

def validate_ip(addr):
    values = [int(i) for i in addr.split('.')]
    if len(values) != 4 or any(filter(lambda x: x < 0 or x > 255, values)):
        raise ValueError("address does not represent an IP")
    return addr

@thought.command('server')
@click.argument("port", type=int) # , help="Port to listen on"
@click.argument("dir", type=pathlib.Path) # , help='directory to store the thoughts in'
@click.argument("--bind", type=validate_ip, default='0.0.0.0') # , help="IPs to accept from"
@click.pass_obj
def thought_server_start(obj, port, dir, bind):
    """starts a thought server bound to the given address and ports, storing in the given directory"""
    run_server((bind, port), dir)

@thought.command('upload')
@click.argument("address", type=lambda x: x.split(":")) # , help="An IP:PORT to a server"
@click.argument("user_id", type=int) # , help="the user uploading the thought"
@click.argument("text", type=str)
@click.argument("pic", type=pathlib.Path)  # not using click.Path on purpose
@click.argument("--timestamp", type=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'),
                default=None) # , help="specifies when the thought thought"
@click.pass_obj
def thought_upload(obj, address, user_id, text, pic, timestamp):
    """
    uploads a thought with the specified contents and timestamp on behalf of the user
    address should be formatted as IP:PORT
    """
    # TODO: add the pic to the upload_thought code
    upload_thought(address, user_id, text, timestamp=timestamp)


@main.group()
@click.pass_context
def webserver(context):
    pass


@webserver.command('start')
@click.argument("PORT", type=int) # help='port to server on
@click.argument("db", type=str) # , help="directory containing all them thoughts to serve"
@click.pass_obj
def webserver_start(obj, port, db):
    """
    starts serving the existing thoughts in the db (filesystem path) on the specified port
    """
    pass  # TODO

if __name__ == '__main__':
    try:
        main(prog_name='aytabu', obj={})
    except Exception as error:
        log(f'ERROR: {error}')
        sys.exit(1)
