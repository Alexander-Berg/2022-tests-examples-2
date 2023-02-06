from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache import resources


class RunNoapachupper(Cube):
    TYPE = TYPE_TEST

    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, name=None, task="projects/upper_search/noapache/build_noapacheupper_data"
    ):
        self._build_noapacheupper_test = build_noapacheupper_test
        self._build_noapacheupper_data = build_noapacheupper_data

        super(RunNoapachupper, self).__init__(
            name=name,
            task=task,
            needs=[build_noapacheupper_test, build_noapacheupper_data],
        )

    @property
    def input_defaults(self):
        return {
            "evlogdump_executable_resource_id": resources.EVLOGDUMP_EXECUTABLE,
            "noapacheupper_config_resource_id": resources.NOAPACHEUPPER_CONFIG,
            "noapacheupper_data_resource_id": self._build_noapacheupper_data.output.resources["NOAPACHEUPPER_DATA"][0].id,
            "noapacheupper_executable_resource_id": self._build_noapacheupper_test.output.resources["NOAPACHE_UPPER"][0].id,
        }

    @property
    def attributes(self):
        return {}


class RunStandaloneNoapacheupper(RunNoapachupper):
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, name=None, task="projects/upper_search/noapache/get_standalone_responses"
    ):

        super(RunStandaloneNoapacheupper, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            name,
            task,
        )

    @property
    def input_defaults(self):
        defaults = super(RunStandaloneNoapacheupper, self).input_defaults
        defaults.update({
            "emulate_response_delay": True,
            "noapacheupper_neh_cache_resource_id": None,
            "ignore_neh_cache_errors": True,
        })

        return defaults
