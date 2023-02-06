from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST


class CheckPrechargeAfterMmap(Cube):
    TYPE = TYPE_TEST

    def __init__(self, build_noapacheupper_test, build_noapacheupper_data):
        self._build_noapacheupper_test = build_noapacheupper_test
        self._build_noapacheupper_data = build_noapacheupper_data

        super(CheckPrechargeAfterMmap, self).__init__(
            name="check_precharge_after_memory_map",
            task="projects/upper_search/noapache/check_precharge_after_mmap",
            needs=[build_noapacheupper_test, build_noapacheupper_data],
            attributes={
                "requirements": {
                    "sandbox": {
                        "platform": "linux",
                        "priority": {
                            "class": "SERVICE",
                            "subclass": "LOW",
                        },
                    },
                },
            },
        )

    @property
    def input_defaults(self):
        return {
            "component": "noapache",
            "read_at_first_request_limit": 1000,
            "binary": self._build_noapacheupper_test.output.resources["NOAPACHE_UPPER"][0].id,
            "noapache_data": self._build_noapacheupper_data.output.resources["NOAPACHEUPPER_DATA"][0].id,
        }
