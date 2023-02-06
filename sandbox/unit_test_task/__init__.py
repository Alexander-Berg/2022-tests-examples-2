# -*- coding: utf-8 -*-

import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.parameters import SandboxStringParameter


class ScenarioName(SandboxStringParameter):
    name = 'scenario'
    description = 'Scenario'
    default_value = ''


class UnitTestTask(SandboxTask):

    type = 'UNIT_TEST'
    SERVICE = True

    input_parameters = [ScenarioName, ]

    def initCtx(self):
        self.ctx['task_status'] = ''

    def do_exception_in_execute(self):
        raise SandboxTaskFailureError('SandboxTaskFailureError was raised')

    def do_nothing(self):
        logging.info('Do nothing')

    unit_test_scnarios = {
        'exception_in_execute': do_exception_in_execute,
        'do_nothing': do_nothing
    }

    def on_execute(self):
        scenario = self.ctx['scenario']
        if scenario:
            if scenario in self.unit_test_scnarios:
                self.unit_test_scnarios[scenario]()
            else:
                raise SandboxTaskFailureError('Unknown scenario {0}'.format(scenario))
        else:
            logging.info('Just log this message')
