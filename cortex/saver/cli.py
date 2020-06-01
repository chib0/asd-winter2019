import functools
import json
import pathlib
import time
import click
import urlpath
from contextlib import suppress

from . import repository, db_dispatcher
from cortex import configuration
from cortex.utils import logging, dispatchers, databases
from cortex.utils.plugin_runner import PluginRunner

module_logger = logging.get_logger(__file__)

@click.group("parsers")
def cli():
    pass


def _get_db_or_die(url):
    db = databases.repository.get_database(url)
    if not db:
        click.prompt(f"Error: no DB for url {url}")
        exit(-1)
    return db

@cli.command('save')
@click.argument('name')
@click.argument('path', type=click.Path(exists=True))
@click.option('-d', '--database', type=urlpath.URL)
def saver(name, path, database):
    db = _get_db_or_die(database)
    saver = functools.partial(repository.get_saver(name).handler, db)
    with logging.log_exception(module_logger, format=lambda x: f"Error running saver {name}: {x}"):
            saver(json.loads(pathlib.Path(path).read_bytes()))


@cli.command('run-saver')
@click.argument('db', type=urlpath.URL)
@click.argument('message_queue', type=urlpath.URL)
def _run_saver(db, message_queue):
    if not (dispatchers.repository.DispatcherRepository.get_repo().has_dispatcher(message_queue) and
            dispatchers.repository.ConsumerRepository.get_repo().has_consumer(message_queue)):
        click.echo(f"Error: no dispatcher/consumer pair for {message_queue.scheme}")
        return -1

    database = _get_db_or_die(db)

    saver_repo = repository.Repository.get()
    tees = []
    for saver in saver_repo.handlers():
        # TODO: consider creating a single consumer for all save topics that can route to correct saver.
        with logging.log_exception(module_logger, to_suppress=(RuntimeError, Exception),
                                   format=lambda x: f"Error running saver service {db}: {x}"):
            consumer = dispatchers.get_topic_consumer(
                configuration.get_parsed_data_topic_name(saver.target),
                message_queue
            )

            tee = dispatchers.tee.Tee(consumer, db_dispatcher.DBDispatcher(database))
            runner = PluginRunner(repository.Repository.get(), json.loads, json.dumps)
            runner.run_with_tee(saver.target, tee)
            tees.append(tee)
    with suppress(KeyboardInterrupt):
        while True:
            time.sleep(1)
    module_logger.info("Stopping all tees...")
    for tee in tees:
        tee.stop()


