from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache import resources


class TestCompareMiddleSearchBinaries(Cube):
    TYPE = TYPE_TEST

    def __init__(self, build_noapache_cube, build_rearrange_cube, build_rearrange_data_fast_cube):
        self._build_noapache_cube = build_noapache_cube
        self._build_rearrange_cube = build_rearrange_cube
        self._build_rearrange_data_fast_cube = build_rearrange_data_fast_cube

        super(TestCompareMiddleSearchBinaries, self).__init__(
            name="blender_performance_vs_prod",
            task="projects/upper_search/noapache/compare_middlesearch_binaries",
            needs=[build_noapache_cube, build_rearrange_cube, build_rearrange_data_fast_cube],
        )

    @property
    def input_defaults(self):
        return {
            "noapacheupper_2_executable_resource_id": self._build_noapache_cube.output.resources["NOAPACHE_UPPER"][0].id,
            "noapacheupper_2_evlogdump_resource_id": self._build_noapache_cube.output.resources["EVLOGDUMP_EXECUTABLE"][0].id,
            "rearrange_data_2_resource_id": self._build_rearrange_cube.output.resources["REARRANGE_DATA"][0].id,
            "rearrange_data_fast_2_resource_id": self._build_rearrange_data_fast_cube.output.resources["REARRANGE_DATA_FAST"][0].id,
            "noapacheupper_1_evlogdump_resource_id": resources.NOAPACHEUPPER_1_EVLOGDUMP,
            "noapache_1_requests_resource_id": resources.NOAPACHE_1_REQUESTS,
            "noapache_2_requests_resource_id": resources.NOAPACHE_2_REQUESTS,
            "launch_mode": "upper",
            "req_count": 15000,
            "calc_mode": "blender",
            "auto_mode": "nocache",
            "enable_auto_diffs": False,
            "fail_on_slowdown_threshold_q95": 500,
            "fail_on_rearrange_slowdown_threshold_q95": 500,
            "nruns": 6,  # temp lightweight
            "noapacheupper_1_max_calc_relev_queue_size": 0,
            "noapacheupper_2_max_calc_relev_queue_size": 0,
            "use_new_calc_eventlog_stats": True,
        }
