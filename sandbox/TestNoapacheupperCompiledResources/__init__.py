# -*- coding: utf-8 -*-

import os
from sandbox import sdk2
from sandbox.projects.websearch.upper.resources import NoapacheUpper as NOAPACHEUPPER_RES_TYPE
from sandbox.projects.websearch.upper.components import Noapacheupper
import sandbox.projects.resource_types as rt
from sandbox.projects.common import requests_wrapper
from sandbox.projects.common.differ import printers, json_differ


class CompiledResourcesDiff(sdk2.Resource):
    """Compiled Resources Diff"""


class TestNoapacheupperCompiledResources(sdk2.Task):
    class Parameters(sdk2.Parameters):
        max_restarts = 10
        kill_timeout = 3600
        resource_path = sdk2.parameters.String('Cgi path to resource')
        with sdk2.parameters.Group('First version build parameters') as noapache1:
            binary_1 = sdk2.parameters.Resource('Noapacheupper executable', resource_type=NOAPACHEUPPER_RES_TYPE)
            config_1 = sdk2.parameters.Resource('Noapacheupper config', resource_type=rt.NOAPACHEUPPER_CONFIG)
            data_1 = sdk2.parameters.Resource('Rearrange data', resource_type=rt.NOAPACHEUPPER_DATA)

        with sdk2.parameters.Group('Second version build parameters') as noapache2:
            binary_2 = sdk2.parameters.Resource('Noapacheupper executable', resource_type=NOAPACHEUPPER_RES_TYPE)
            config_2 = sdk2.parameters.Resource('Noapacheupper config', resource_type=rt.NOAPACHEUPPER_CONFIG)
            data_2 = sdk2.parameters.Resource('Rearrange data', resource_type=rt.NOAPACHEUPPER_DATA)

    def on_execute(self):
        params = self._get_packed_params()
        strings_to_diff = []
        for kwargs in params:
            noapacheupper = Noapacheupper(self, **kwargs)
            with noapacheupper:
                text = requests_wrapper.get_r('http://localhost:{port}/yandsearch?info=get_resource:name:{path}'.format(
                    port=noapacheupper.port, path=self.Parameters.resource_path)).text
                strings_to_diff.append(text)
        self._create_diff(strings_to_diff)

    def _create_diff(self, strings_to_diff):
        output_path = os.path.join(os.getcwd(), 'diff')
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        CompiledResourcesDiff(self, 'Diff', output_path)
        printer = printers.PrinterToHtml(output_path)
        differ = json_differ.JsonDiffer(printer)
        differ.compare_single_pair(*strings_to_diff)
        printer.finalize()

    def _get_packed_params(self):
        return [
            {
                'binary': self.Parameters.binary_1,
                'config': self.Parameters.config_1,
                'upper_data': self.Parameters.data_1,
            },
            {
                'binary': self.Parameters.binary_2,
                'config': self.Parameters.config_2,
                'upper_data': self.Parameters.data_2,
            },
        ]
