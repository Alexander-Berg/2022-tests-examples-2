# -*- coding: utf-8 -*-

import os.path

from sandbox.sandboxsdk.process import run_process
import sandbox.sandboxsdk.parameters as sb_params

from sandbox.projects.common.build.YaMake import YaMakeTask
import sandbox.projects.common.build.parameters as build_params
from sandbox.projects.common.environments import ValgrindEnvironment


valgrind_params = [
    '--tool=memcheck',
    '--leak-check=full',
    '--track-origins=yes',
    '--error-exitcode=1',
    '--gen-suppressions=all',
    '-v',
]

valgrind_supp = 'sandbox/projects/TestWithValgrind/valgrind.supp'


class Targets(sb_params.SandboxStringParameter):
    name = 'targets'
    description = 'Targets (semicolon separated)'
    group = 'Project params'
    required = True
    default_value = None


class Executables(sb_params.SandboxStringParameter):
    name = 'executables'
    description = 'Test executables (semicolon separated)'
    group = 'Project params'
    required = False
    default_value = None


class ValgrindParams(sb_params.SandboxStringParameter):
    name = 'valgrind_params'
    description = 'Valgrind command line parameters'
    group = 'Project params'
    required = False
    default_value = ' '.join(valgrind_params)


class TestWithValgrind(YaMakeTask):
    """
    Сборка и запуск тестов под Valgrind
    """

    type = 'TEST_WITH_VALGRIND'

    input_parameters = [
        build_params.ArcadiaUrl,
        build_params.ArcadiaPatch,
        build_params.DefinitionFlags,

        Targets,
        Executables,
        ValgrindParams,
    ]

    def get_build_type(self):
        return 'valgrind'

    def get_targets(self):
        return self.ctx['targets'].split(';')

    def post_build(self, source_dir, output_dir, pack_dir):
        valgrind = ValgrindEnvironment()
        valgrind.prepare()

        bin_dir = os.path.join(output_dir, 'bin')
        if self.ctx['executables']:
            executables = self.ctx['executables'].split(';')
        else:
            executables = self.find_ut_executables(bin_dir)

        for executable in executables:
            valgrind_cmd = 'valgrind %s --suppressions=%s %s' % (
                self.ctx['valgrind_params'],
                os.path.join(source_dir, valgrind_supp),
                os.path.join(bin_dir, executable),
            )

            run_process(
                valgrind_cmd,
                log_prefix='valgrind',
                wait=True,
                check=True,
                shell=True,
                outputs_to_one_file=True,
            )

    def find_ut_executables(self, path):
        return run_process(
            'find -H . -type f -perm /a+x -name "*-ut"',
            work_dir=path,
            shell=True,
            outs_to_pipe=True
        ).communicate()[0].rstrip().split()


__Task__ = TestWithValgrind
