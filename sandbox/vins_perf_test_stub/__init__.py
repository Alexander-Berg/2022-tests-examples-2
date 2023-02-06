# -*- coding: utf-8 -*-

import json
import logging
import os
import subprocess

from sandbox import sdk2


LOGGER = logging.getLogger('VinsPerfTestStubTask')

STUB_PATH = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/projects/bassrm/vins_perf_test_stub/data.json'
STUB_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
STUB_NAME = 'stub.json'


class VinsPerfTestStubTask(sdk2.Task):
    '''
        Run VinsPerfTest Stub Task
    '''

    class Parameters(sdk2.Task.Parameters):
        arc_rev = sdk2.parameters.Integer(
            'Arcadia revision',
            default=6012402,
            required=True
        )

    def execute_with_logging(self, cmd):
        logging.debug('Running {}'.format(cmd))

        s = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
        exitcode = None
        while True:
            line = s.stderr.readline()
            exitcode = s.poll()

            if (not line) and (exitcode is not None):
                break
            logging.debug("pid %s: %s", os.getpid(), line.strip())

        logging.debug("pid %s: finished", os.getpid(), cmd)
        return exitcode

    def on_execute(self):

        LOGGER.debug('Downloading stub data')
        cmd_text = 'svn cat -r' + str(self.Parameters.arc_rev) + ' '
        self.execute_with_logging(cmd_text + STUB_PATH + ' > ' + STUB_NAME)

        path_to_src = os.path.abspath(STUB_NAME)

        LOGGER.info('OPEN JSON FILE')
        with open(path_to_src) as json_file:
            stub_data = json.load(json_file)

        LOGGER.info('SAVE STUB DATA')
        self.Context.vins_perf_test_scores = stub_data
        LOGGER.info('FINISH')
