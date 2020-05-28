import contextlib
import json
import pathlib

import click
import urlpath


from cortex.parsers import repository
from cortex.utils import logging,\
                            dispatchers

from cortex.core import snapshot_xcoder
from cortex.utils.plugin_runner import PluginRunner

module_logger = logging.get_logger(__file__)

@click.group("parsers")
def cli():
    pass


@cli.command('parse')
@click.argument('name')
@click.argument('path', type=click.Path(exists=True))
def parse(name, path):
    with logging.log_exception(module_logger, format=lambda x: f"Error running parser {name}: {x}"):
            runner = PluginRunner(repository.Repository.get(), snapshot_xcoder.snapshot_decoder)
            out = runner.run(name, pathlib.Path(path).read_bytes())
            click.echo(json.dumps(str(out)))


@cli.command('run-parser')
@click.argument('name')
@click.argument('url', type=urlpath.URL)
def _run_parser(name, url):
    if not (dispatchers.repository.DispatcherRepository.get_repo().has_dispatcher(url) and
            dispatchers.repository.ConsumerRepository.get_repo().has_consumer(url)):
        click.echo(f"Error: no dispatcher/consumer pair for {url.scheme}")
        return -1

    with logging.log_exception(module_logger, to_suppress=(RuntimeError, Exception),
                               format=lambda x: f"Error running parser {name}: {x}"):
        runner = PluginRunner(repository.Repository.get(), snapshot_xcoder.snapshot_decoder, json.dumps)
        out = runner.run_with_uri(name, uri=url)



