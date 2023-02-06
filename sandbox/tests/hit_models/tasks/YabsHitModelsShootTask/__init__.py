from sandbox.projects.common import binary_task
from sandbox.projects.resource_types import AbstractResource
from sandbox.projects.runtime_models.tests.hit_models.modules.sut.adapters.sandbox import HitModelsSUTSandboxAdapter

from sandbox.projects.yabs.qa.task_factory.simple_shoot_task import factory as simple_shoot_task_factory
from sandbox.projects.yabs.qa.dolbilo_module.simple.adapters.sandbox import DolbiloModuleSandboxAdapter
from sandbox.projects.yabs.qa.yt_uploader_module.adapters.sandbox import ShootResultsYtUploaderGenericSandboxAdapter
from sandbox.projects.yabs.qa.ammo_module.requestlog.adapters.general.sandbox import AmmoRequestlogModuleGeneralSandboxAdapter
from sandbox.common.types import resource as ctr
from sandbox.common.types import client as ctc


class YabsHitModelsResponseDump(AbstractResource):
    restart_policy = ctr.RestartPolicy.DELETE


simple_shoot_task = simple_shoot_task_factory(
    HitModelsSUTSandboxAdapter,
    AmmoRequestlogModuleGeneralSandboxAdapter,
    DolbiloModuleSandboxAdapter,
    YabsHitModelsResponseDump,
    'YABS_HIT_MODELS',
    ShootResultsYtUploaderGenericSandboxAdapter
)


class YabsHitModelsShootTask(simple_shoot_task, binary_task.LastBinaryTaskRelease):
    class Requirements(simple_shoot_task.Requirements):
        ram = 142072
        # TODO(@aleosi) process only on intel until custom float comparator will be made
        client_tags = ctc.Tag.Group.INTEL
