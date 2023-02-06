# -*- coding: utf-8 -*-

import os
import signal

from sandbox.projects import resource_types
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.parameters import LastReleasedResource


class RtyserverUtResourceId(LastReleasedResource):
    resource_type = resource_types.RTYSERVER_UNITTEST
    name, description = 'rtyserver_ut_resource_id', 'RTYServer ut binary'


class TestRTYServerUT(SandboxTask):
    type = 'TEST_RTYSERVER_UT'

    input_parameters = [RtyserverUtResourceId]

    def parseLog(self, logfile):
        cnt_good, cnt_fail = 0, 0
        t_failed = []
        for line in open(logfile, 'r').readlines():
            if line.startswith('[FAIL]'):
                cnt_fail += 1
                t_failed.append(line.split()[1].split(':')[-1])
            elif line.startswith('[good]'):
                cnt_good += 1
        self.set_info('Tests count:\ngood: %s\nfailed: %s\n' % (cnt_good, cnt_fail))
        if cnt_fail > 0:
            self.set_info('failed tests: %s' % ''.join(t_failed))
            raise SandboxTaskFailureError('some tests failed')

    def on_execute(self):
        test_path = self.sync_resource(self.ctx['rtyserver_ut_resource_id'])

        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            process.communicate()
            self.ctx['task_result_type'] = 'timeout'

        try:
            run_process(test_path,
                        timeout=800, timeout_sleep=1,
                        log_prefix='test_execution',
                        on_timeout=on_timeout)
        finally:
            self.parseLog(os.path.join(self.log_path(), 'test_execution.out.txt'))

        self.set_info('Done')


__Task__ = TestRTYServerUT
