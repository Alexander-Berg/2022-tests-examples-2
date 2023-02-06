# -*- coding: utf-8 -*-
import logging
import traceback
import os

from sandbox import common

from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import LastReleasedResource
from sandbox.sandboxsdk.paths import get_logs_folder
from sandbox.sandboxsdk.paths import get_unique_file_name
from sandbox.sdk2.helpers.gdb import get_html_view_for_logs_file

from .test_neh import TNehTest


class NehcParameter(LastReleasedResource):
    name = 'nehc_resource_id'
    description = 'nehc utility'
    resource_type = 'NEHC_EXECUTABLE'


class TestNeh(SandboxTask):
    """
        test arcadia/library/cpp/neh protocols, - run test_neh.py module/script, which use console utility nehc
        for make/handle misc neh requests
    """

    type = 'TEST_NEH'

    input_parameters = [NehcParameter, ]

    def on_execute(self):
        neh_test = TNehTest()
        neh_test.Nehc = self.sync_resource(self.ctx['nehc_resource_id'])
        neh_test.Verbose = 3

        out_name = 'test_neh.out.txt'
        err_name = 'test_neh.err.txt'

        stdout_path = None
        stderr_path = None
        stdout = None
        stderr = None

        def close_neh_logs():
            if stdout:
                stdout.close()
            if stderr:
                stderr.close()

            if os.path.getsize(stderr_path) > 0:
                html_err_log = get_html_view_for_logs_file(
                    err_name, err_name, channel.task._log_resource.id)
                self.set_info(
                    "neh stderr is available in task logs:<br />{0}"
                    .format(html_err_log), do_escape=False)

        try:
            stdout_path = get_unique_file_name(get_logs_folder(), out_name)
            stderr_path = get_unique_file_name(get_logs_folder(), err_name)
            stdout = open(stdout_path, 'w')
            stderr = open(stderr_path, 'w')
        except IOError as e:
            close_neh_logs()
            raise common.errors.TaskError(
                'Cannot open log files: '
                'stdout file: {0}, stderr file: {1}. Error: {2}'.format(stdout_path, stderr_path, e)
            )

        # redirect test verbose output to our logs
        def log1(s):
            self.set_info(s)
            logging.info(s)
            stdout.write(s)

        def log2(s):
            stdout.write(s)

        def log3(s):
            stdout.write(s)

        neh_test.Log1 = log1
        neh_test.Log2 = log2
        neh_test.Log3 = log3

        try:
            neh_test.Run()
        except Exception as e:
            err = "Internal test error: Caught run-time exception " \
                "in test_neh module: {0}\n".format(e) + traceback.format_exc()
            logging.error(err)
            stderr.write(err + neh_test.ErrorsText())
            if neh_test.LastResult:
                stderr.write("Last log:\n" + neh_test.LastResult.Log.getvalue())
            close_neh_logs()
            raise SandboxTaskFailureError(err)

        if neh_test.Failed == 0:
            success = "Successfully pass {0} tests".format(len(neh_test.Results))
            self.set_info(success)
            logging.info(success)
        else:
            stderr.write(neh_test.ErrorsText())
            close_neh_logs()
            raise SandboxTaskFailureError(
                "Failed {0} tests from {1} (see logfile {2} for details)"
                .format(neh_test.Failed, len(neh_test.Results), stderr_path))

        close_neh_logs()


__Task__ = TestNeh
