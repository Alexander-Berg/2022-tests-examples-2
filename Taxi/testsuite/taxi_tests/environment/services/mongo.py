import os

from taxi_tests.environment import utils


SERVICE_NAME = 'mongo'

DEFAULT_CONFIG_SERVER_PORT = 27118
DEFAULT_MONGOS_PORT = 27217
DEFAULT_SHARD_PORT = 27119


class Service:
    def __init__(
            self,
            worker_id,
            build_dir,
            mongos_port=None,
            config_server_port=None,
            shard_port=None,
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
        self.mongos_port = mongos_port or DEFAULT_MONGOS_PORT
        self.config_server_port = (
            config_server_port or DEFAULT_CONFIG_SERVER_PORT
        )
        self.shard_port = shard_port or DEFAULT_SHARD_PORT
        self.env = {
            'MONGO_TMPDIR': self.working_dir,
            'MONGOS_PORT': str(self.mongos_port),
            'CONFIG_SERVER_PORT': str(self.config_server_port),
            'SHARD_PORT': str(self.shard_port),
        }
        if env is not None:
            self.env.update(env)

    def ensure_started(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_START, self.env)

    def stop(self):
        utils.service_command(SERVICE_NAME, utils.COMMAND_STOP, self.env)


def get_connection_string(port):
    return 'mongodb://localhost:%s/' % port
