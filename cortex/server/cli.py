import click
from cortex.server import server
from cortex.utils import logging


# ----=========== CLI ===========----
@click.group()
def cli():
    pass

@cli.command("run-server")
@click.option("--host", "-h")
@click.option("--port", "-p", type=int)
@click.argument('publish_url')
def run_server_cli(host, port, publish_url):
    with logging.log_exception(logging.get_module_logger(__file__), to_suppress=(Exception,)):
        server.run_server_with_url(host or "127.0.0.1", port or 8080, publish_url)



if __name__ == "__main__":
    cli()
