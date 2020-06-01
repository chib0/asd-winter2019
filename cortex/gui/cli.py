import click

from .website import run_server

@click.group()
def cli():
    pass

@cli.command('run-server')
@click.option("-h", "--host", type=str, default='127.0.0.1')
@click.option("-p", "--port", type=int, default=8000)
@click.option("-H", "--api-host", type=str, default='127.0.0.1')
@click.option("-P", "--api-port", type=int, default=5000)
def run_server_cli(host, port, api_host, api_port):
    run_server(host, port, api_host, api_port)