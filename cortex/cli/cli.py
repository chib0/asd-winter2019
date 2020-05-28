import click

from . import get_consumer

@click.group()
@click.option("-h", "--host", default="localhost")
@click.option("-p", "--port", default="8000", type=int)
@click.pass_context
def cli(ctx, host, port):
    ctx.ensure_object(dict)
    #we're setting ctx.obj to match the signature of the api_consumer kwarg options for host, port, etc.
    ctx.obj['consumer'] = get_consumer(host, port)

@cli.command()
@click.pass_context
def get_users(ctx):
    click.echo(ctx.obj['consumer'].get_users())


@cli.command()
@click.argument('user_id')
@click.pass_context
def get_user(ctx, user_id):
    click.echo(ctx.obj['consumer'].get_user(user_id))


@cli.command()
@click.argument('user_id')
@click.pass_context
def get_snapshots(ctx, user_id):
    click.echo(ctx.obj['consumer'].get_snapshots(user_id))


@cli.command()
@click.argument('user_id')
@click.argument('snapshot_id_or_timestamp')
@click.pass_context
def get_snapshot(ctx, user_id, snapshot_id_or_timestamp):
    click.echo(ctx.obj['consumer'].get_snapshot(user_id, snapshot_id_or_timestamp))


@click.command
@click.argument('user_id')
@click.argument('snapshot_id_or_timestamp')
@click.argument('result')
@click.pass_context
def get_result(ctx, user_id, snapshot_id_or_timestamp, result):
    click.echo(ctx.obj['consumer'].get_result( user_id, snapshot_id_or_timestamp, result))


@click.command
@click.argument('user_id')
@click.argument('snapshot_id_or_timestamp')
@click.argument('result')
@click.pass_context
def get_result_data(ctx, user_id, snapshot_id_or_timestamp, result):
    click.echo(ctx.obj['consumer'].get_result_data(user_id, snapshot_id_or_timestamp, result))

