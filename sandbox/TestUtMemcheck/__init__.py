# -*- coding: utf-8 -*-

import sandbox.common.types.client as ctc

from sandbox.projects import resource_types
from sandbox.projects.common.environments import ValgrindEnvironment
from sandbox.projects.common.search import memcheck
from sandbox.projects.common import utils

from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk import process as sp
from sandbox.sandboxsdk.task import SandboxTask


class UtExecutable(parameters.ResourceSelector):
    name = 'ut_executable'
    description = 'UT executable'
    resource_type = resource_types.SEARCH_META_UT_EXECUTABLE
    required = True


class TestUtMemcheck(SandboxTask):
    """
    Run unittest under memcheck (Valgrind) and fail on any severe errors encountered.
    See also https://st.yandex-team.ru/SEARCH-1307
    """
    type = 'TEST_UT_MEMCHECK'
    # Do not run on old Ubuntu to prevent failures like in SEARCH-2276
    client_tags = ctc.Tag.Group.LINUX & ~ctc.Tag.LINUX_LUCID

    input_parameters = [
        UtExecutable,
        memcheck.XmlOutputParameter,
        memcheck.ValgrindSuppressionsParameter,
    ]

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        memcheck.create_output(self)

    def on_execute(self):
        ValgrindEnvironment().prepare()
        ut_executable = self.sync_resource(self.ctx[UtExecutable.name])
        valgrind_cmd = memcheck.get_valgrind_command_params(self)
        valgrind_cmd += [
            ut_executable,
            '--print-times',
        ]
        process = sp.run_process(
            valgrind_cmd,
            check=False,
            log_prefix='memcheck',
            outputs_to_one_file=True,
        )
        utils.show_process_tail(process)
        memcheck.analyze_errors(self)


__Task__ = TestUtMemcheck
