#!/usr/bin/env python
# coding: utf-8
import os
import logging

import sandbox.sandboxsdk.process as process
import sandbox.projects.common.arcadia.sdk as arcadia_sdk
import sandbox.projects.common.constants as consts

from sandbox.sdk2 import yav
from sandbox.projects.common.build.YaExec import YaExec


def symlink(existing_path, link_path):
    process.run_process(['ln', '-s', existing_path, link_path])


class TestEnvironmentCleanup(YaExec):
    type = "TEST_ENVIRONMENT_CLEANUP"

    def on_execute(self):
        program_path = 'testenv/core/bin/tools/tools'
        env_vars = self.get_env_vars()

        if program_path:
            build_target = 'testenv/core'

            with arcadia_sdk.mount_arc_path(self.ctx[consts.ARCADIA_URL_KEY]) as arcadia_dir:
                logging.debug("Arcadia src dir %s", arcadia_dir)

                logging.info("Target to build %s", build_target)
                build_return_code = arcadia_sdk.do_build(
                    'ya', arcadia_dir, [build_target], clear_build=False, results_dir=arcadia_dir)

                logging.info("Build returned %s", build_return_code)

                testenv_conf_dir = os.path.join(os.getcwd(), '.te_conf')

                secret = yav.Secret('sec-01et88det5evkwjnhd999c19gs')
                config = secret.data()['production_config']
                with open(testenv_conf_dir, 'w') as teconf:
                    teconf.write(config)

                symlink(os.path.join(arcadia_dir, program_path), 'tetools')
                process.run_process(
                    list('./tetools run_cleanup --config {}'.format(testenv_conf_dir).split()),
                    log_prefix='program',
                    outputs_to_one_file=False,
                    shell=True,
                    work_dir=arcadia_dir,
                    environment=env_vars,
                )


__Task__ = TestEnvironmentCleanup
