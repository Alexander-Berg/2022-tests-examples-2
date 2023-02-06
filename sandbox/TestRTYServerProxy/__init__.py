# -*- coding: utf-8 -*-

import os
import re
import signal

from sandbox.sandboxsdk.parameters import LastReleasedResource, SandboxStringParameter

from sandbox.projects import resource_types
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.process import run_process


class PSearchproxyId(LastReleasedResource):
    resource_type = resource_types.RTYSERVER_SEARCHPROXY_UT
    name, description = 'rtyserver_searchproxy_resource_id', 'RTYServer searchproxy binary'


class PTestName(SandboxStringParameter):
    name, description = 'test_name', 'test name or group'
    default_value = '--print-before-suite'


class TestRTYServerProxy(SandboxTask):
    type = 'TEST_RTYSERVER_PROXY'

    input_parameters = [PSearchproxyId, PTestName]

    def initCtx(self):
        self.ctx['perf_time'] = ''

    def checkTime(self):
        log_file = os.path.join(self.log_path(), 'test_execution.err.txt')
        if os.path.exists(log_file):

            found = False
            for line in open(log_file).readlines():
                if found:
                    self.ctx['perf_time'] = line[:-1]  # remove last 's'
                    break
                if re.search('TLoadTestWarmup::TestWarmup', line):
                    found = True

    def checkPorts(self):
        try:
            run_process(["netstat", "-a"], log_prefix='ports_after_task', check=True, wait=True, shell=True)
        except MemoryError as e:
            self.set_info("exception:  %s" % e)

        try:
            run_process(["ps", "-auxww"], log_prefix='processes_after_task', check=True, wait=True, shell=True)
        except MemoryError as e:
            self.set_info("exception:  %s" % e)

    def on_execute(self):
        server_test = self._read_resource(self.ctx['rtyserver_searchproxy_resource_id'])
        if server_test.arch != self.arch:
            raise SandboxTaskFailureError('Incorrect server resource #%s arch "%s" on host with arch "%s".' %
                                          (server_test.id, server_test.arch, self.arch))

        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            process.communicate()
            self.ctx['task_result_type'] = 'timeout'

        server_test_path = server_test.abs_path()

        test_name = self.ctx.get('test_name', '--print-before-suite')
        try:
            run_process([server_test_path, '--print-times', test_name],
                        timeout=7200,
                        log_prefix='test_execution',
                        on_timeout=on_timeout)
        finally:
            self.checkPorts()

        self.checkTime()

        self.set_info('Done')


__Task__ = TestRTYServerProxy
