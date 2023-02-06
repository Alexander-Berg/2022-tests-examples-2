from sandbox.common import errors as ce
from sandbox.projects.common.build import YaMake
from sandbox import sdk2
from sandbox.sandboxsdk import parameters


class PrParam(parameters.SandboxIntegerParameter):
    name = 'pr'
    description = 'pr id'
    default_value = 0


class TestFakeZipatcher(YaMake.YaMakeTask):
    type = 'TEST_FAKE_ZIPATCHER'
    cores = 1
    input_parameters = [PrParam]

    def on_execute(self):
        review_id = self.ctx.get('pr', 0)
        patch_info = sdk2.Task.current.agentr.patch_info(review_id)
        if not patch_info:
            raise ce.TaskError("Pull request {} not found".format(review_id))

        self.set_info("Pull request {} found: {}".format(review_id, patch_info))

__Task__ = TestFakeZipatcher
