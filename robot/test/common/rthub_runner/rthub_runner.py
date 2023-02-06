# -*- coding: utf-8 -*-

import logging
import requests
from robot.rthub.protos.config_pb2 import TConfig
import robot.rthub.library.web_client.python.client as client
from robot.rthub.test.common.rthub_runner.sensors import load_json_sensors
from robot.rthub.test.common.rthub_runner.lb_reader import LBReader
from robot.rthub.test.common.rthub_runner.lb_writer import LBWriter
from library.recipes.common import start_daemon, stop_daemon
import google.protobuf.text_format as pbtext
import yatest.common
from yatest.common.network import PortManager
import shutil
import os

RTHUB_PID_FILE = 'rthub.pid'
logger = logging.getLogger("rthub_runner")


class RTHubRunner:
    def __init__(
        self,
        rthub_bin,
        original_config,
        test_data,
        output_path
    ):
        self._rthub_bin = rthub_bin
        self._original_config = original_config
        self._config = yatest.common.work_path('config.pb.txt')
        self._test_data = test_data
        self._output_path = output_path
        self._obj_config = self._read_config()
        self._port_manager = PortManager()
        self._mon_port = str(self._port_manager.get_port())
        self._web_server_port = None
        self._logbroker_port = None

    def _read_config(self):
        config = TConfig()
        with open(self._original_config, 'r') as f:
            pbtext.Parse(f.read(), config)
        return config

    def save_config(self):
        content = pbtext.MessageToString(self._obj_config)
        with open(self._config, 'w') as f:
            f.write(content)
        logger.info(content)

    def get_config(self):
        return self._config

    def get_config_content(self):
        return pbtext.MessageToString(self._obj_config)

    def set_env_variable(self, name, value):
        size = len(self._obj_config.Environment.Variable)
        i = 0
        changed = False
        while i < size:
            if self._obj_config.Environment.Variable[i].Name == name:
                self._obj_config.Environment.Variable[i].Value = value
                changed = True
            i = i + 1

        if not changed:
            self._obj_config.Environment.Variable.add()
            self._obj_config.Environment.Variable[size].Name = name
            self._obj_config.Environment.Variable[size].Value = value

    def _clear_field(self, config, field_name):
        if config.HasField(field_name):
            config.ClearField(field_name)

    def update_config(self, udfs_path, proto_path, resources_path,
                      libraries_path, queries_path, threads_count, max_input_message_size=None):

        if os.path.exists(yatest.common.work_path('protos')):
            shutil.rmtree(yatest.common.work_path('protos'))

        if not os.path.isdir(yatest.common.work_path('protos')):
            shutil.copytree(proto_path, yatest.common.work_path('protos'))

        for root, dirnames, filenames in os.walk(yatest.common.work_path('protos')):
            for filename in filenames:
                if not filename.endswith('.proto') and not filename.endswith('.ev'):
                    logger.info('removing: ' + os.path.join(root, filename))
                    os.remove(os.path.join(root, filename))

        if udfs_path:
            self._obj_config.UdfsPath = udfs_path
        self._obj_config.ProtoPath = yatest.common.work_path('protos')
        if resources_path:
            self._obj_config.ResourcesPath = resources_path

        if libraries_path:
            self._obj_config.LibrariesPath = libraries_path

        self._obj_config.YqlPath = queries_path

        if threads_count:
            if self._obj_config.Limits.HasField('WorkerThreadsCount'):
                self._obj_config.Limits.WorkerThreadsCount = threads_count

        if max_input_message_size:
            if self._obj_config.Limits.HasField('MaxInputMessageSize'):
                self._obj_config.Limits.MaxInputMessageSize = max_input_message_size

        self._clear_field(self._obj_config.Limits, 'CpuOversubscription')
        self._clear_field(self._obj_config, 'MultipleInstancesOnSingleHost')
        self._clear_field(self._obj_config, 'ExecutionTimeoutMillis')
        self._clear_field(self._obj_config, 'InitialExecutionTimeoutMillis')
        self._clear_field(self._obj_config, 'InstanceStateFilePath')
        self._clear_field(self._obj_config, 'UnifiedAgentUri')

        self._try_use_logbroker_recipe()

    def get_logbroker_port(self):
        return self._logbroker_port

    def create_lb_reader(self, topic):
        return LBReader(self._logbroker_port, topic)

    def create_lb_writer(self, topic):
        return LBWriter(self._logbroker_port, topic)

    def _try_use_logbroker_recipe(self):
        lb_port = int(os.getenv('LOGBROKER_PORT', '0'))
        if not lb_port:
            return

        self._logbroker_port = lb_port

        def _use_local_logbroker(pq):
            pq.Server = 'localhost'
            pq.DataPort = lb_port
            pq.ControlPort = lb_port

        self._obj_config.ClearField('LogBroker')
        for ch in self._obj_config.Channel:
            for input in ch.Input:
                _use_local_logbroker(input.Source)

            for output in ch.Output:
                for pq in output.Queue:
                    _use_local_logbroker(pq)

    def _allocate_web_server_address(self):
        self._web_server_port = self._port_manager.get_port()
        return "localhost:{}".format(self._web_server_port)

    def get_web_client(self, topic, output_name):
        assert self._web_server_port is not None
        return client.WebClient('localhost', self._web_server_port, topic, output_name)

    def get_json_sensors(self, path='rthub'):
        return load_json_sensors('http://localhost:{port}/{path}/json'.format(port=self._mon_port, path=path))

    def _compose_rthub_cmd(self, binary=True, web_server_input_format=None):
        rthub_cmd = [
            self._rthub_bin,
            '--config', self._config,
            '--port', self._mon_port
        ]

        if self._test_data:
            rthub_cmd.extend(['--input-directory', self._test_data])

        if self._output_path:
            rthub_cmd.extend(['--output-directory', self._output_path])

        if binary:
            rthub_cmd.append('--use-binary-format')

        if web_server_input_format is not None:
            address = self._allocate_web_server_address()
            rthub_cmd.extend(['--web-server', address])
            rthub_cmd.append('--web-write-to-pq')
            rthub_cmd.append(
                '--web-binary-format' if web_server_input_format == 'binary' else '--web-binary-batch-format')
        return rthub_cmd

    def _is_alive_daemon(self):
        try:
            r = requests.get("http://localhost:{}".format(self._mon_port))
            if r.status_code == 200:
                logger.info("RTHub ping: 200!")
                return True

            logger.info("RTHub ping: {} : {}".format(r.status_code, r.text))
        except Exception as e:
            logger.info("RTHub ping: {}".format(e))
        return False

    def run_rthub(self, binary=True, web_server_input_format=None, as_daemon=False):
        # web_server_input_format is one of: None, 'binary', 'binary_batch'
        rthub_cmd = self._compose_rthub_cmd(binary=binary, web_server_input_format=web_server_input_format)

        logger.info("RTHub cmd: {}".format(rthub_cmd))
        logger.info("Running RTHub...")

        if as_daemon:
            start_daemon(rthub_cmd, None, self._is_alive_daemon, RTHUB_PID_FILE)
        else:
            yatest.common.execute(
                rthub_cmd
            )

    def stop_daemon(self):
        with open(RTHUB_PID_FILE) as f:
            pid = f.read()

        if not stop_daemon(pid):
            logger.info("pid is dead: {}".format(pid))
