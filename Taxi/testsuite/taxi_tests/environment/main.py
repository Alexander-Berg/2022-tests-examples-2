import argparse
import contextlib
import subprocess
import sys

from taxi_tests.environment import control


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--build-dir', help='Build directory path', required=True,
    )
    parser.add_argument(
        '--services',
        nargs='+',
        help='List of services (default: %(default)s)',
        default=['mongo', 'redis', 'postgresql'],
    )
    parser.set_defaults(handler=None)

    subparsers = parser.add_subparsers()

    command_parser = subparsers.add_parser('start', help='Start services')
    command_parser.set_defaults(handler=_command_start)

    command_parser = subparsers.add_parser('stop', help='Stop services')
    command_parser.set_defaults(handler=_command_stop)

    command_parser = subparsers.add_parser(
        'run', help='Run command with services started',
    )
    command_parser.add_argument('command', nargs='+', help='Command to run')
    command_parser.set_defaults(handler=_command_run)

    args = parser.parse_args()

    if args.handler is None:
        parser.error('No command given')

    env = control.TestsuiteEnvironment(
        worker_id='master', build_dir=args.build_dir,
    )
    args.handler(env, args)


def _command_start(env, args):
    for service_name in args.services:
        env.ensure_started(service_name)


def _command_stop(env, args):
    for service_name in args.services:
        env.stop_service(service_name)


def _command_run(env, args):
    _command_start(env, args)
    with contextlib.closing(env):
        exit_code = subprocess.call(args.command)
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
