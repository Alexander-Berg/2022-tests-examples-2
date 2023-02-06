from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache.noapache_tests.run import RunStandaloneNoapacheupper
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache import resources


class SubsourceRequestsStandaloneNoapacheupper(RunStandaloneNoapacheupper):  # TODO: add dependent compare test cube
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data,
        name="web_kubr_subsource_requests_standalone", task="projects/upper_search/noapache/get_standalone_eventlog"
    ):
        self._noapache_requests = resources.NOAPACHE_REQUESTS["subsource"]

        super(SubsourceRequestsStandaloneNoapacheupper, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            name=name,
            task=task,
        )

    @property
    def input_override(self):
        return {
            "noapache_requests_resource_id": self._noapache_requests,
            "get_responses_from_binary": True,
            "emulate_response_delay": False,
            "requests_limit": 100,
            "noapacheupper_apphost_mode": True,
        }

    @property
    def attributes(self):
        parent = super(SubsourceRequestsStandaloneNoapacheupper, self).attributes
        override = {
            "requirements": {
                "sandbox": {
                    "platform": "linux",
                    "priority": {
                        "class": "SERVICE",
                        "subclass": "LOW",
                    },
                },
            },
        }

        return CubeInput.update_recursive(
            parent,
            override
        )
