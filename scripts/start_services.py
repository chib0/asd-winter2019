import contextlib
import pathlib
import subprocess
import time

import docker
import click
try:
    from cortex import configuration
except ImportError:
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))
    from cortex import configuration

@click.group()
def services():
    pass


def _run_image(to_run, dock=None, detach=False, re_run=False):
    dock = dock or docker.from_env()
    for i in dock.containers.list():
        if to_run['image'] in i.image.tags:
            if not re_run:
                print(f"Already running: {i.name}")
                return
            click.echo(f'stopping {i.name}...')
            i.stop()
    click.echo(f"starting {to_run['image']}...")
    #TODO: consider changing to **to_run
    container = dock.containers.run(to_run['image'], detach=detach, ports=to_run['ports'], hostname=to_run['hostname'],
                                    volumes=to_run.get('volumes', None) )
    click.echo(f"started: {container.name}")


def start_service(name, detach, re_run):
    images = configuration.get_config()[configuration.CONFIG_SERVICE_DOCKER_IMAGES]
    dock = docker.from_env()
    if name == 'all':
        if not detach:
            click.echo("Error: can't run all images without detaching")
            exit(-1)
        for i in images.values():
            _run_image(i, dock, detach, re_run)
    else:
        _run_image(images[name], dock, detach=detach, re_run=re_run)


@services.command('start-service')
@click.argument('name', type=click.Choice(['db', 'mq', 'all']))
@click.option('-t', '--type', help='TODO specific type (mongo vs postgres) of service to start')
@click.option('--detach/--attach', default=True)
@click.option('-r', '--re-run/--no-re-run')
def _start_service(name, type, detach, re_run):
    start_service(name, detach, re_run)

RABBIT_MQ = 'rabbitmq://localhost:5672'
MONGO_DB = 'mongodb://localhost:27017'
def _build_parsers_cmdlines(parsers):
    return [['cortex.parsers', 'run-parser', i, RABBIT_MQ] for i in parsers]

def _build_system_processes():
    out = _build_parsers_cmdlines(('color-image', 'pose', 'feelings', 'depth-image'))
    out.append(['cortex.saver', 'run-saver', MONGO_DB, RABBIT_MQ])
    out.append(['cortex.core.server', 'run-server', '-h', '127.0.0.1', '-p', '8080', RABBIT_MQ])
    out.append(['cortex.api', 'run-server', '-h', '127.0.0.1', '-p', '5000', '-d', MONGO_DB])
    return out

@services.command('start-system')
def start_system():
    start_service('all', True, True)
    time.sleep(1)
    running = []
    for i in _build_system_processes():
        running.append(subprocess.Popen(['pyhon', '-m'] + i))

    with contextlib.suppress(KeyboardInterrupt):
        while all(proc.poll() is None for proc in running):
            time.sleep(1)

    for proc in running:
        if proc.poll() is None:
            proc.kill()
        else:
            click.echo(f"{proc} ended before killing everything")


if __name__ == "__main__":
    services()
