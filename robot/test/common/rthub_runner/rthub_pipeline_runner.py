# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
from robot.rthub.protos.config_pb2 import TConfig
import google.protobuf.text_format as pbtext
import yatest.common
import shutil
import os

logger = logging.getLogger("rthub_pipeline_runner")


class RTHubPipelineRunner:
    def __init__(self, original_config):
        self._rthub_pipeline_bin = yatest.common.binary_path('robot/rthub/tools/pipeline_check/rthub_pipeline_check')
        self._original_config = original_config
        self._config = yatest.common.work_path('config.pb.txt')
        self._obj_config = self._read_config()

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

    def _clear_field(self, config, field_name):
        if config.HasField(field_name):
            config.ClearField(field_name)

    def update_config(self, udfs_path, proto_path, resources_path,
                      libraries_path, queries_path):

        protos_path = yatest.common.work_path('protos')
        if not os.path.isdir(protos_path):
            shutil.copytree(proto_path, protos_path)

        for root, dirnames, filenames in os.walk(protos_path):
            for filename in filenames:
                if not filename.endswith('.proto') and not filename.endswith('.ev'):
                    os.remove(os.path.join(root, filename))

        if udfs_path:
            self._obj_config.UdfsPath = udfs_path
        self._obj_config.ProtoPath = protos_path
        if resources_path:
            self._obj_config.ResourcesPath = resources_path

        if libraries_path:
            self._obj_config.LibrariesPath = libraries_path

        self._obj_config.YqlPath = queries_path
        self._clear_field(self._obj_config, 'Environment')

    def run(self):
        cmd = [
            self._rthub_pipeline_bin,
            '--config', self._config
        ]

        logger.info("RTHubPipeline cmd: {}".format(cmd))

        subprocess.check_call(
            cmd,
            stdout=sys.stderr,
            stderr=subprocess.STDOUT
        )
