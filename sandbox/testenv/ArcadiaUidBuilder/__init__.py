# -*- coding: utf-8 -*-

import json
import logging
import os
import shlex
import subprocess

from sandbox import sdk2
from sandbox.projects.common.arcadia import sdk as arcadia_sdk
import sandbox.projects.common.build.parameters as build_parameters


class ArcadiaUidBuilder(sdk2.Task):
    class Parameters(sdk2.Parameters):
        checkout_arcadia_from_url = build_parameters.ArcadiaUrl()
        arcadia_patch = build_parameters.ArcadiaPatch()
        targets = sdk2.parameters.String('targets')
        ya_make_args = sdk2.parameters.String('ya make args')

    def on_execute(self):
        with arcadia_sdk.mount_arc_path(self.Parameters.checkout_arcadia_from_url) as arcadia_path:
            if self.Parameters.arcadia_patch:
                arcadia_sdk.apply_patch(
                    self,
                    arcadia_path,
                    self.Parameters.arcadia_patch,
                    arcadia_path,
                    False,
                )
            command_template = '{ya_path} make -j0 -G {ya_make_args} {targets}'
            command = command_template.format(
                ya_path=os.path.join(arcadia_path, 'ya'),
                ya_make_args=self.Parameters.ya_make_args,
                targets=self.Parameters.targets,
            )
            logging.info('run command %s', command)
            p = subprocess.Popen(
                shlex.split(command),
                cwd=arcadia_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logging.info('command finished')
            stdout, stderr = p.communicate()
        logging.error('ya make error messages:')
        for line in stderr.split('\n'):
            logging.error(line)
        if p.returncode != 0:
            raise Exception('ya make failed with code %s', p.returncode)
        logging.info('start parsing')
        graph = json.loads(stdout)
        self.Context.uids = json.dumps(graph['result'])
        self.Context.save()
