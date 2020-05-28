import click
from cortex.utils import databases
from . import run_api_server


from cortex.utils.logging import get_module_logger, log_exception

logger = get_module_logger(__path__)

@click.group()
def cli():
    pass

@cli.command()
@click.option('-h', '--host', default='0.0.0.0')
@click.option('-p', '--port', default=5000, type=int)
@click.option('-d', '--database', default='mongodb://localhost:27017', type=str)
def run_server(*args, **kwargs):
    with log_exception(logger, to_suppress=(ValueError, Exception)):
        run_api_server(*args, **kwargs)

