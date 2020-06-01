import click
from . import upload_sample

@click.group()
def client():
    pass


@client.command('upload-sample')
@click.option('-h', '--host', default="127.0.0.1", help="server ip/name, defaults to localhost")
@click.option('-p', '--port', default="8000", help="server port, defaults to 8000")
@click.argument('sample_path')
def upload_cli(host, port, sample_path):
    """
    uploads the thoughts in the sample file to the server
    """
    return upload_sample(host, port, sample_path)



client()
