"""
The thought server is basically a flask app, that handles REST api calls.
The request data are bson dicts. I could've used protobuf but then I wouldn't've had to work to keep this and sample
reader disjoint.

What's it gonna do?
The server generally just gets a message, writes it to the disk, and publishes a message that it has been received.
The message then goes into a parser that extrects logic info (like images), and puts it in files, republishes results
More and more parsers will see more and more messages as parsing takes place.
"""
import click

import threading

from cortex import utils, configuration
from cortex.utils import logging, dispatchers
from cortex.core import cortex_rest_server

module_logger = logging.get_module_logger(__file__)

def get_server(publish, encoder):
    return cortex_rest_server.get_server(publish,
                                         message_encoder=encoder or configuration.raw_message_encoder())

def _run_server(host, port, publish, encoder=None, run_threaded=False):
    module_logger.debug("getting server...")
    server = get_server(publish, encoder)
    server_args = dict(host=host, port=port)
    if run_threaded:
        t = threading.Thread(name=configuration.get_config()[configuration.CONFIG_SERVER_THREAD_NAME],
                         target=server.run,
                         kwargs=server_args)
        module_logger.info(f"starting {server} on {host}:{port} on thread...")
        t.start()
    else:
        module_logger.info(f"starting {server} on {host}:{port} ...")
        server.run(**server_args)

# ----=========== CLI ===========----
@click.group()
def cli():
    pass

@cli.command("run-server")
@click.option("--host", "-h")
@click.option("--port", "-p", type=int)
@click.argument('publish_url')
def run_server_cli(host, port, publish_url):
    publisher = None
    with logging.log_exception(logger=module_logger, to_suppress=(Exception,)):
        publisher = dispatchers.repository.DispatcherRepository.get_repo().get_dispatcher(publish_url,
                                                                                          configuration.get_config()[configuration.CONFIG_SERVER_PUBLISH_TOPICS])
    if not publisher:
        click.prompt("couldn't find publisher for the given URL")
        exit(-1)

    module_logger.info(f"got publisher {publisher}")

    with utils.logging.log_exception(logger=module_logger, to_suppress=(Exception,)):
        _run_server(host, port, publisher)


if __name__ == "__main__":
    cli()