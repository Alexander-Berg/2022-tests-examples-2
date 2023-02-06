import logging

import click

from ppadb.client import Client as AdbClient

logger = logging.getLogger(__name__)


class Context:
    @classmethod
    def for_device_serial(cls, serial):
        client = AdbClient()
        devices = client.devices()

        if not devices:
            raise ValueError('No adb devices!')
        else:
            if serial:
                for d in devices:
                    if d.serial == serial:
                        device = d
                        logger.info('Using specified device %s' % device.serial)
                        break
                else:
                    raise ValueError('Device %s not found among connected' % serial)
            else:
                device = devices[0]
                logger.info('Using default device %s' % device.serial)

        return cls(client, device)

    def __init__(self, client, device):
        self.client = client
        self.device = device


@click.group()
@click.pass_context
@click.option('--verbose', is_flag=True, default=False)
@click.option('--device', help='What device to use, defaults to the only one')
def cli(ctx, device, verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='>>> %(asctime)s %(levelname)-8s %(name)-10s %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='>>> %(asctime)s %(levelname)-8s %(name)-10s %(message)s')

    ctx.obj = Context.for_device_serial(device)


@cli.command()
@click.pass_obj
@click.option('--name', required=True, help='Directive name')
@click.option('--dry-run', is_flag=True, default=False, help='Dont actually execute command')
@click.option(
    '--payload',
    type=click.Path(file_okay=True, dir_okay=False, readable=True, allow_dash=False, resolve_path=True),
    required=True,
    help='File with directive payload',
)
def execute(ctx, name, payload, dry_run):
    """
    Executes directive with given name taking payload from a file

    Pushes the given file to the device in /sdcard/Download/ (we got permission to access those) and fires a directive to read from it
    """

    # TODO: maybe use https://developer.android.com/reference/android/content/Context.html#getCacheDir%28%29 instead of Download?
    target_path = '/sdcard/Download/centaur.last_directive'
    logger.info("Executing directive <%s> on device <%s>" % (name, ctx.device.serial))
    logger.debug("Pushing payload to <%s>" % (target_path,))
    ctx.device.push(payload, target_path)

    # FIXME: when adding next command make this better
    command_template = '''am broadcast -a ru.yandex.quasar.centaur_app.EXECUTE_ACTION -p ru.yandex.quasar.centaur_app --es name '%s' --es 'payload.path' '%s' '''
    command = command_template % (name, target_path)

    if dry_run:
        logger.info("Would execute command <%s>" % command)
    else:
        logger.debug("Executing command <%s>" % command)
        result = ctx.device.shell(command)
        logger.info("Result: <%s>" % result)


def main():
    cli()
