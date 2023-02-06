from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube, CubeInput
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST
from sandbox.projects.common.constants import constants as common_const


class LaunchArcadiaTestsForRearrangeDynamic(Cube):
    TYPE = TYPE_TEST

    def __init__(self, new_tag_cube):
        self._new_tag_cube = new_tag_cube

        super(LaunchArcadiaTestsForRearrangeDynamic, self).__init__(
            name="launch_arcadia_tests_for_rearrange_dynamic",
            task="YA_MAKE",
            needs=[new_tag_cube],
            attributes={
                "requirements": {
                    "ram": 24 * 1024 ** 3,  # in Bytes
                    "disk": 80 * (1024 ** 3),  # in Bytes
                },
            },
        )

    @property
    def input_defaults(self):
        return {
            common_const.ARCADIA_URL_KEY: "{}/arcadia".format(
                CubeInput.format_cube_output_value(self._new_tag_cube.output.svn_data.svn_paths.tag),
            ),
            "targets": ";".join([
                "search/web/rearrs_upper/tests",
                "search/web/rearrs_upper/rearrange.dynamic",
            ]),
            "clear_build": False,
            "test": True,
            "report_tests_only": True,
            "disable_test_timeout": True,
            "cache_test_results": False,
            "tests_retries": 2,
        }
