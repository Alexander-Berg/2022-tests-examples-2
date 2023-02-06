import os

from taxi_tests.environment import utils


SERVICE_NAME = 'postgresql'

DEFAULT_PORT = 5432


class Service:
    def __init__(self, worker_id, build_dir, env=None):
        self.worker_id = worker_id
        self.working_dir = os.path.join(
            build_dir, 'testsuite', 'tmp', SERVICE_NAME,
        )
        self.configs_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'configs',
            'postgresql',
        )
        self.env = {
            'POSTGRESQL_CONFIGS_DIR': self.configs_dir,
            'POSTGRESQL_PORT': str(DEFAULT_PORT),
        }
        if env is not None:
            self.env.update(env)

    def ensure_started(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_START, self.env)

    def stop(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_STOP, self.env)


def get_connection_string(worker_id='master'):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return (
        'host=/tmp/testsuite-postgresql/%s/ port=%d user=testsuite dbname='
    ) % (worker_suffix, DEFAULT_PORT)
