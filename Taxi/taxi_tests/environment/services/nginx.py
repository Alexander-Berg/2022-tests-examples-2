import os

from taxi_tests.environment import utils
from taxi_tests.utils import gennginx


SERVICE_NAME = 'nginx'

DEFAULT_PORT = 8009


class Service:
    def __init__(self, worker_id, build_dir, port=None, env=None):
        self.worker_id = worker_id
        working_dir = self.working_dir = os.path.join(
            build_dir, 'testsuite', 'tmp', SERVICE_NAME,
        )
        template_dir = os.path.join(build_dir, 'testsuite', 'configs')
        if worker_id != 'master':
            self.working_dir = os.path.join(working_dir, '_' + worker_id)
            self.configs_dir = os.path.join(self.working_dir, 'configs')
        else:
            self.working_dir = working_dir
            self.configs_dir = template_dir
        self.working_dir = self.working_dir
        self.template = os.path.join(template_dir, gennginx.TEMPLATE_FILENAME)
        self.port = port or DEFAULT_PORT
        self.env = {
            'NGINX_TMPDIR': self.working_dir,
            'NGINX_CONFIGS_DIR': self.configs_dir,
        }
        if env is not None:
            self.env.update(env)

    def ensure_started(self):
        if self.worker_id != 'master':
            self._generate_configs()

        utils.service_command(SERVICE_NAME, utils.COMMAND_START, self.env)

    def stop(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_STOP, self.env)

    def _generate_configs(self):
        os.makedirs(self.configs_dir, exist_ok=True)
        gennginx.process_template(
            self.template, self.configs_dir, self.port, self.worker_id,
        )
