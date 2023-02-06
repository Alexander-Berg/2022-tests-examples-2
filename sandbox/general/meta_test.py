from sandbox.projects.common.constants import constants as common_const
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import internal
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import build


class MetaTest(build.YaMake2):
    TYPE = internal.TYPE_TEST

    def __init__(self, targets, **kwargs):
        super(MetaTest, self).__init__(targets=targets, artifacts=None, resource_types="", **kwargs)

    @property
    def input_defaults(self):

        result = super(MetaTest, self).input_defaults

        result.update({
            common_const.CHECK_RETURN_CODE: True,
            common_const.FAILED_TESTS_CAUSE_ERROR: False,
            common_const.JUNIT_REPORT: True,
            common_const.TESTS_REQUESTED: True,
        })

        return result
