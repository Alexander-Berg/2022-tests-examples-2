import os
import subprocess


COMMAND_START = 'start'
COMMAND_STOP = 'stop'

DOCKERTEST_WORKER = os.getenv('DOCKERTEST_WORKER', '')


class CommandFailed(Exception):
    pass


def get_scripts_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts'))


def service_command(service_name, command, environment=None):
    env = os.environ.copy()
    if environment:
        env.update(environment)
    process = subprocess.run(
        [
            os.path.join(get_scripts_dir(), 'service-%s' % service_name),
            command,
        ],
        env=env,
    )
    if process.returncode != 0:
        raise CommandFailed(
            'Service \'%s\' exited with code %d. Command: %s'
            % (service_name, process.returncode, command),
        )
