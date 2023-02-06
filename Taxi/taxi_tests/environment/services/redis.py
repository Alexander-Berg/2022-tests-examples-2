import os

from taxi_tests.environment import utils
from taxi_tests.utils import genredis


SERVICE_NAME = 'redis'

MASTERS_NUMBER = 2
SLAVES_NUMBER = 3

DEFAULT_HOST = 'localhost'
MASTER_DEFAULT_PORT = 16379
SENTINEL_DEFAULT_PORT = 26379
SLAVE_DEFAULT_PORT = 16380


class NotEnoughPorts(Exception):
    pass


class Service:
    def __init__(
            self, worker_id, build_dir, masters_ports=None, slaves_ports=None,
            sentinel_port=None, env=None):
        self.worker_id = worker_id
        working_dir = os.path.join(
            build_dir, 'testsuite', 'tmp', SERVICE_NAME,
        )
        if worker_id != 'master':
            self.working_dir = os.path.join(working_dir, '_' + worker_id)
            self.configs_dir = os.path.join(self.working_dir, 'configs')
        else:
            self.working_dir = working_dir
            self.configs_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', '..', 'configs',
            )
        self.masters_ports = masters_ports or [MASTER_DEFAULT_PORT]
        self.slaves_ports = slaves_ports or [SLAVE_DEFAULT_PORT]
        self.sentinel_port = sentinel_port or SENTINEL_DEFAULT_PORT
        self.env = {
            'REDIS_TMPDIR': self.working_dir,
            'REDIS_CONFIGS_DIR': self.configs_dir,
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
        if (len(self.masters_ports) != MASTERS_NUMBER and
                len(self.slaves_ports) != SLAVES_NUMBER):
            raise NotEnoughPorts(
                'Need exactly %d masters and %d slaves!' % (
                    MASTERS_NUMBER, SLAVES_NUMBER,
                ),
            )
        genredis.generate_redis_configs(
            output_path=self.configs_dir,
            master0_port=self.masters_ports[0],
            master1_port=self.masters_ports[1],
            slave0_port=self.slaves_ports[0],
            slave1_port=self.slaves_ports[1],
            slave2_port=self.slaves_ports[2],
            sentinel_port=self.sentinel_port,
        )
