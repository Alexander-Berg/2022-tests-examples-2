# -*- coding: utf-8 -*-
import logging
import os
import os.path
import time

from sandbox import common
from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
from sandbox.sandboxsdk.environments import PipError
from sandbox.sandboxsdk.environments import VirtualEnvironment
from sandbox.sandboxsdk.parameters import SandboxBoolParameter, SandboxStringParameter
from sandbox.sandboxsdk.paths import copy_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.task import SandboxTask
import sandbox.common.types.client as ctc


class ArgLocalRunMode(SandboxBoolParameter):
    name = 'local_run_mode'
    description = 'local run mode or not'
    default_value = False


class ArgSubScriptName(SandboxStringParameter):
    name = 'subscript_name'
    description = 'subscript name'
    required = True


class ArgSubScriptRequirements(SandboxStringParameter):
    name = 'subscript_requirements'
    description = 'subscript requirements'
    required = False


class ArgSubScriptArgs(SandboxStringParameter):
    name = 'subscript_args'
    description = 'subscript args'
    required = False


class TestFromExternalScript(SandboxTask):
    type = 'TEST_FROM_EXTERNAL_SCRIPT'
    input_parameters = [
        ArgLocalRunMode, ArgSubScriptName, ArgSubScriptRequirements, ArgSubScriptArgs
    ]

    client_tags = ctc.Tag.Group.LINUX

    def _setup_mapreduce(self):
        resource = apihelpers.get_last_resource(resource_types.MAPREDUCE_EXECUTABLE)
        if not resource:
            raise common.errors.SandboxEnvironmentError("mapreduce_binary not found")

        path = self.sync_resource(resource)
        os.environ["PATH"] += os.pathsep + os.path.dirname(path)

    def process_file(self, fname):
        fname = fname.strip(' \n\r\t')
        if len(fname) < 1:
            return None

        if self.ctx[ArgLocalRunMode.name]:
            sub_script_fname = fname
            copy_path(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), sub_script_fname),
                os.path.join(self.abs_path(), sub_script_fname)
            )
        else:
            sep_pos = fname.rfind('/')
            arcadia_part = "arcadia:/arc/trunk/" + fname[:sep_pos]
            sub_script_fname = fname[sep_pos + 1:]
            copy_path(
                os.path.join(Arcadia.get_arcadia_src_dir(arcadia_part), sub_script_fname),
                os.path.join(self.abs_path(), sub_script_fname)
            )
        return sub_script_fname

    def on_execute(self):
        import sys
        logging.info("sys.path: {}".format(sys.path))
        original_python_path = os.environ['PYTHONPATH']
        logging.info(common.rest.Client._external_auth)
        token = common.rest.Client._external_auth.task_token

        n_attempts = 10
        timeout = 10

        for attempt_i in xrange(n_attempts):
            try:
                with VirtualEnvironment() as venv:
                    venv.pip('-U pip')
                    venv.pip('yandex-yt==0.6.90.post0 yandex-yt-yson-bindings-skynet mapreducelib')
                    if len(self.ctx[ArgSubScriptRequirements.name]) > 0:
                        venv.pip(self.ctx[ArgSubScriptRequirements.name])
                    self._setup_mapreduce()

                    logging.info("env: {}".format(str(os.environ)))

                    sub_script_fname = None
                    files_to_look_for = self.ctx[ArgSubScriptName.name].split(';')
                    logging.info(u'files to look for: {}'.format(files_to_look_for))
                    for fname in files_to_look_for:
                        res = self.process_file(fname)
                        if sub_script_fname is None:
                            sub_script_fname = res

                    # !beware - hack for using sandboxsdk inside jobs
                    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + original_python_path
                    # !beware tocken passed
                    os.environ['SANDBOX_TOKEN'] = token
                    run_process([venv.executable, sub_script_fname] + self.ctx[ArgSubScriptArgs.name].split(),
                                log_prefix="external_script")
            except PipError:
                logging.exception('Attempt {}. Failed to interact with VENV'.format(attempt_i))
                time.sleep(timeout)
            else:
                break


__Task__ = TestFromExternalScript
