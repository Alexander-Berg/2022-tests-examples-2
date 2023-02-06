from parameters import HitModelsSUTParameters, HitModelsSUTParametersSecondRun
from sandbox.projects.runtime_models.tests.hit_models.modules.sut.adapters.interface import HitModelsSUTAdapterInterface
from sandbox.projects.runtime_models.tests.hit_models.modules.sut import HitModelsSUT
from sandbox.projects.yabs.qa.adapter_base.sandbox import SandboxAdapterBase

import os


class HitModelsSUTSandboxAdapter(HitModelsSUTAdapterInterface, SandboxAdapterBase):
    def __init__(self, parameters, task_instance, work_dir=None):
        SandboxAdapterBase.__init__(self, parameters, task_instance)
        self._work_dir = work_dir if work_dir else os.getcwd()

    @staticmethod
    def get_init_parameters_class(second_run=False):
        return HitModelsSUTParameters if not second_run else HitModelsSUTParametersSecondRun

    def get_hit_models_binary_path(self):
        return self.sync_resource(self.parameters.service_binary)

    def get_hit_models_layer_path(self):
        return self.sync_resource(self.parameters.service_layer)

    def get_hit_models_archive_models_path(self):
        return self.sync_resource(self.parameters.service_model_archive)

    def get_work_dir(self):
        return self._work_dir

    def create_module(self):
        return HitModelsSUT(self)
