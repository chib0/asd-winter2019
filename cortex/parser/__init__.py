import json
import pathlib
import threading
import time

import click
import urlpath


from cortex.parser import repository
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


def run_parser(name, url, blocking=True):
    if not (dispatchers.repository.DispatcherRepository.get_repo().has_dispatcher(url) and
            dispatchers.repository.ConsumerRepository.get_repo().has_consumer(url)):
        module_logger.error(f"Error: no dispatcher/consumer pair for {url.scheme}")
        return -1

    with logging.log_exception(module_logger, to_suppress=(RuntimeError, Exception),
                               format=lambda x: f"Error running parser {name}: {x}"):
        runner = PluginRunner(repository.Repository.get(), snapshot_xcoder.snapshot_decoder, json.dumps)
        runner.run_with_uri(name, uri=url)

@cli.command('run-parser')
@click.argument('name')
@click.argument('url', type=urlpath.URL)
def _run_parser(name, url):
    run_parser(name, url)

@cli.command('start-all')
@click.argument('url', type=urlpath.URL)
def _run_all_parsers(url):
    repo = repository.Repository.get()
    waiting = []
    for parser in repo.handlers():
        t = threading.Thread(target=run_parser, args=(parser.target, url), kwargs=dict(blocking=False))
        t.start()
        waiting.append(t)

    with logging.log_exception(module_logger, to_suppress=(KeyboardInterrupt,),
                               format=lambda x: f"stopping all parsers..."):
        while True:
            time.sleep(1)
