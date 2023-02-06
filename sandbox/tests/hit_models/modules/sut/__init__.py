from sandbox.projects.yabs.qa.module_base import ModuleBase

from sandbox.projects.runtime_models.tests.hit_models.components.hit_models import YabsHitModels


class HitModelsSUT(YabsHitModels, ModuleBase):
    def __init__(self, adapter):
        ModuleBase.__init__(self, adapter)
        YabsHitModels.__init__(
            self,
            task=adapter.get_task_instance(),
            binary_path=adapter.get_hit_models_binary_path(),
            layer_path=adapter.get_hit_models_layer_path(),
            archive_path=adapter.get_hit_models_archive_models_path()
        )

    def __enter__(self):
        YabsHitModels.__enter__(self)
        return self

    def __exit__(self, *args):
        YabsHitModels.__exit__(self, *args)

    def flush_state(self):
        YabsHitModels.flush_state(self)

    def is_active(self):
        return self.process.poll() is None

    def get_port(self):
        return YabsHitModels.get_port(self)
