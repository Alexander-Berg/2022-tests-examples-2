from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube, CubeInput
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST
from sandbox.projects.common.constants import constants as common_const


class TestRtccDiff(Cube):
    TYPE = TYPE_TEST

    def __init__(self, new_tag_cube, build_rtcc_bundle_cube):
        self._new_tag_cube = new_tag_cube
        self._build_rtcc_bundle_cube = build_rtcc_bundle_cube

        super(TestRtccDiff, self).__init__(
            name="rtcc_diff_test",
            task="projects/upper_search/noapache/build_rtcc_diff",
            needs=[build_rtcc_bundle_cube],
        )

    @property
    def input_defaults(self):
        return {
            common_const.ARCADIA_URL_KEY: "{}/arcadia".format(
                CubeInput.format_cube_output_value(self._new_tag_cube.output.svn_data.svn_paths.tag)
            ),
            "production_noapache_new_bundle": self._build_rtcc_bundle_cube.output.resources["RTCC_BUNDLE_NOAPACHE"][0].id,
            "production_noapache_new_cache": self._build_rtcc_bundle_cube.output.resources["RTCC_CACHE_NOAPACHE"][0].id,
            "ctype": "production_noapache",
        }
