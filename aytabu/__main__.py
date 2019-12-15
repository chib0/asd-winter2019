import os
import sys
import traceback

import click

import foobar


class Log:

    def __init__(self):
        self.quiet = False
        self.traceback = False

    def __call__(self, message):
        if self.quiet:
            return
        if self.traceback and sys.exc_info(): # there's an active exception
            message += os.linesep + traceback.format_exc().strip()
        click.echo(message)


log = Log()


@click.group()
@click.version_option(foobar.version)
@click.option('-q', '--quiet', is_flag=True)
@click.option('-t', '--traceback', is_flag=True)
def main(quiet=False, traceback=False):
    log.quiet = quiet
    log.traceback = traceback


@main.group()
@click.pass_context
def foo(context):
    context.obj['foo'] = foobar.Foo()


@foo.command('run')
@click.pass_obj
def foo_run(obj):
    foo = obj['foo']
    log(foo.run())


@foo.command('inc')
@click.argument('x', type=int)
@click.pass_obj
def foo_inc(obj, x):
    foo = obj['foo']
    log(foo.inc(x))


@foo.command('add')
@click.argument('x', type=int)
@click.argument('y', type=int)
@click.pass_obj
def foo_add(obj, x, y):
    foo = obj['foo']
    log(foo.add(x, y))


@main.group()
@click.pass_context
def bar(context):
    context.obj['bar'] = foobar.Bar()


@bar.command('run')
@click.option('-o', '--output')
@click.option('-u', '--uppercase', is_flag=True)
@click.pass_obj
def bar_run(obj, output=None, uppercase=False):
    bar = obj['bar']
    result = bar.run()
    if uppercase:
        result = result.upper()
    if output:
        with open(output, 'w') as writer:
            writer.write(result)
    else:
        log(result)


@bar.command('error')
def bar_error():
    raise RuntimeError('something went terribly wrong :[')


if __name__ == '__main__':
    try:
        main(prog_name='foobar', obj={})
    except Exception as error:
        log(f'ERROR: {error}')
        sys.exit(1)
