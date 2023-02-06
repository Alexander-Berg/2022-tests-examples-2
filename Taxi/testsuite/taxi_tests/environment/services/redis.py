import os

from taxi_tests.environment import utils
from taxi_tests.utils import genredis


SERVICE_NAME = 'redis'

DEFAULT_HOST = os.getenv('HOSTNAME', '::1')
MASTERS_DEFAULT_PORTS = [16379, 16389]
SENTINEL_DEFAULT_PORT = 26379
SLAVES_DEFAULT_PORTS = [16380, 16390, 16381]


class NotEnoughPorts(Exception):
    pass


class Service:
    def __init__(
            self,
            worker_id,
            build_dir,
            masters_ports=None,
            slaves_ports=None,
            sentinel_port=None,
            env=None,
    ):
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
        self.configs_dir = os.path.join(self.working_dir, 'configs')
        self.masters_ports = masters_ports or MASTERS_DEFAULT_PORTS
        self.slaves_ports = slaves_ports or SLAVES_DEFAULT_PORTS
        self.sentinel_port = sentinel_port or SENTINEL_DEFAULT_PORT
        self.env = {
            'REDIS_TMPDIR': self.working_dir,
            'REDIS_CONFIGS_DIR': self.configs_dir,
        }
        if env is not None:
            self.env.update(env)

    def ensure_started(self):
        self._generate_configs()

        utils.service_command(SERVICE_NAME, utils.COMMAND_START, self.env)

    def stop(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_STOP, self.env)

    def _generate_configs(self):
        os.makedirs(self.configs_dir, exist_ok=True)
        if len(self.masters_ports) != len(MASTERS_DEFAULT_PORTS) and len(
                self.slaves_ports,
        ) != len(SLAVES_DEFAULT_PORTS):
            raise NotEnoughPorts(
                'Need exactly %d masters and %d slaves!'
                % (len(MASTERS_DEFAULT_PORTS), len(SLAVES_DEFAULT_PORTS)),
            )
        genredis.generate_redis_configs(
            output_path=self.configs_dir,
            host=DEFAULT_HOST,
            master0_port=self.masters_ports[0],
            master1_port=self.masters_ports[1],
            slave0_port=self.slaves_ports[0],
            slave1_port=self.slaves_ports[1],
            slave2_port=self.slaves_ports[2],
            sentinel_port=self.sentinel_port,
        )
