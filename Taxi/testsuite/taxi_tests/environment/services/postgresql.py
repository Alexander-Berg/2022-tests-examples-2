import os

from taxi_tests.environment import utils


SERVICE_NAME = 'postgresql'

DEFAULT_PORT = 5433


class Service:
    def __init__(self, worker_id, build_dir, port=None, env=None):
        self.worker_id = worker_id
        working_dir = os.path.join(
            build_dir,
            'testsuite',
            'tmp',
            utils.DOCKERTEST_WORKER,
            SERVICE_NAME,
        )
        if worker_id != 'master':
            self.working_dir = os.path.join(working_dir, '_' + worker_id)
        else:
            self.working_dir = working_dir
        self.configs_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..',
            'configs',
            'postgresql',
        )
        self.env = {
            'POSTGRESQL_TMPDIR': self.working_dir,
            'POSTGRESQL_CONFIGS_DIR': self.configs_dir,
            'POSTGRESQL_PORT': str(port or DEFAULT_PORT),
        }
        if env is not None:
            self.env.update(env)

    def ensure_started(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_START, self.env)

    def stop(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_STOP, self.env)


def get_connection_string(port=DEFAULT_PORT):
    return 'host=localhost port=%d user=testsuite dbname=' % port
