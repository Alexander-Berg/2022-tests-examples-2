# -*- coding: utf-8 -*-

import logging
import shutil

from sandbox.projects import resource_types
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import ResourceSelector


class MyMatrixnetExecutableParameter(ResourceSelector):
    name = 'matrixnet_resource_id'
    description = 'matrixnet binary'
    resource_type = 'MATRIXNET_EXECUTABLE'
    required = True


class MyMatrixnetTestPoolParameter(ResourceSelector):
    name = 'test_pool_resource_id'
    description = 'matrixnet test pool'
    resource_type = 'MATRIXNET_TEST_POOL'
    required = True


def init_config(f):
    config = dict()
    for line in f:
        line = line.rstrip()
        pos = line.find('\t')
        if pos == -1 and line.startswith('learn command'):
            pos = len('learn command')
        if pos == -1:
            continue
        config[line[:pos]] = line[pos + 1:].strip()
    return config


class TestMatrixnet(SandboxTask):
    type = 'TEST_MATRIXNET'

    input_parameters = (
        MyMatrixnetExecutableParameter,
        MyMatrixnetTestPoolParameter,
    )

    def on_execute(self):
        logging.info('on_execute started...')
        shutil.copy(self.sync_resource(self.ctx['matrixnet_resource_id']), 'matrixnet')
        pool_archive_path = self.sync_resource(self.ctx['test_pool_resource_id'])
        run_process(['tar', 'zxf', pool_archive_path, '--strip-components=1'], log_prefix='extract')
        config = init_config(open('config.tsv', 'r'))
        run_process(config['learn command'], log_prefix='learn')
        run_process(['./matrixnet', '-A', '-f', 'learn.tsv', '-t', 'test.tsv'], log_prefix='test')

        matrixnet_predictions = self.create_resource(config['learn command'], 'test.tsv.matrixnet', resource_types.MATRIXNET_TESTING_PREDICTIONS)
        self.ctx['matrixnet_predictions_resource_id'] = matrixnet_predictions.id


__Task__ = TestMatrixnet
