from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache.noapache_tests.run import RunNoapachupper, RunStandaloneNoapacheupper
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache import utils as noapache_utils
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache import resources


class GetApphostResponsesStandaloneNoapacheupper(RunStandaloneNoapacheupper):
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, test_type, noapache_type="upper",
        name="responses_standalone", task="projects/upper_search/noapache/get_standalone_responses"
    ):
        noapache_utils.validate_noapache_test_types(test_type, noapache_type)

        self._noapache_type = noapache_type
        self._noapache_requests = resources.NOAPACHE_REQUESTS[noapache_type]

        _name = "{}_".format(test_type)
        _name += name
        _name += noapache_type

        super(GetApphostResponsesStandaloneNoapacheupper, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            name=_name,
            task=task,
        )

    @property
    def input_defaults(self):
        defaults = super(GetApphostResponsesStandaloneNoapacheupper, self).input_defaults
        defaults.update({
            "noapache_requests_resource_id": self._noapache_requests,
            "run_mode": self._noapache_type,
            "emulate_response_delay": True,
            "scale_process_count": 80,
            "noapacheupper_apphost_mode": True,
            "tool_converter": self._build_noapacheupper_test.output.resources["APP_HOST_TOOL_CONVERTER_EXECUTABLE"][0].id,
            "tool_proto2hr": resources.TOOL_PROTO2HR,
            "app_host_ops": resources.APPHOST_OPS,
            "noapacheupper_metric_constraint": "rearrange_errors == 0",
        })

        return defaults

    @property
    def attributes(self):
        parent = super(GetApphostResponsesStandaloneNoapacheupper, self).attributes
        override = {
            "requirements": {
                "sandbox": {
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


class GetResponsesStandaloneNoapacheupperRelease(GetApphostResponsesStandaloneNoapacheupper):  # TODO: add dependent compare test cube
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, test_type, noapache_type="upper",
        name="responses_standalone", task="projects/upper_search/noapache/get_standalone_responses"
    ):
        super(GetResponsesStandaloneNoapacheupperRelease, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            test_type,
            noapache_type,
            name=name,
            task=task,
        )

    @property
    def input_override(self):
        return {
            "check_responses_stability": True,
        }


class GetResponsesStandaloneNoapacheupperDebug(GetApphostResponsesStandaloneNoapacheupper):
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, test_type, noapache_type="upper",
        name="responses_standalone_debug", task="projects/upper_search/noapache/get_standalone_responses"
    ):
        super(GetResponsesStandaloneNoapacheupperDebug, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            test_type,
            noapache_type,
            name=name,
            task=task,
        )

    @property
    def attributes(self):
        parent = super(GetResponsesStandaloneNoapacheupperDebug, self).attributes
        override = {
            "requirements": {
                "cores": 4,
                "ram": 64 * 1024 ** 3,
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


class GetResponsesStandaloneNoapacheupperProdFlowDebug(RunNoapachupper):
    def __init__(
        self, build_noapacheupper_test, build_noapacheupper_data, noapache_type, grpc=False, images=False, video=False, unistat=False,
        task="projects/upper_search/noapache/get_standalone_responses"
    ):
        noapache_utils.validate_noapache_type(noapache_type)

        self._noapache_type = noapache_type
        self._grpc = grpc

        name = "get_responses_standalone_{}".format(noapache_type) if "debug" not in build_noapacheupper_test.name.lower() else "get_responses_standalone_debug_{}".format(noapache_type)

        if grpc:
            name += "_grpc"

        if unistat:
            name += "_unistat"

        if images:
            name += "_images"
            self._noapache_requests = resources.NOAPACHE_REQUESTS["images"]
        elif video:
            name += "_video"
            self._noapache_requests = resources.NOAPACHE_REQUESTS["video"][noapache_type]
        elif grpc:
            self._noapache_requests = resources.NOAPACHE_REQUESTS["grpc"]
        else:
            self._noapache_requests = resources.NOAPACHE_REQUESTS[noapache_type]

        super(GetResponsesStandaloneNoapacheupperProdFlowDebug, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            name=name,
            task=task,
        )

    @property
    def input_defaults(self):
        defaults = super(GetResponsesStandaloneNoapacheupperProdFlowDebug, self).input_defaults
        defaults.update({
            "evlogdump_executable_resource_id": resources.EVLOGDUMP_EXECUTABLE,
            "noapacheupper_config_resource_id": resources.NOAPACHEUPPER_CONFIG,
            "noapacheupper_data_resource_id": self._build_noapacheupper_data.output.resources["NOAPACHEUPPER_DATA"][0].id,
            "noapacheupper_executable_resource_id": self._build_noapacheupper_test.output.resources["NOAPACHE_UPPER"][0].id,
            "emulate_response_delay": True,
            "noapacheupper_apphost_mode": True,
            "ignore_neh_cache_errors": True,
            "scale_process_count": 80,
            "tool_proto2hr": resources.TOOL_PROTO2HR,  # required for apphost mode
            "app_host_ops": resources.APPHOST_OPS,
            "tool_converter": self._build_noapacheupper_test.output.resources["APP_HOST_TOOL_CONVERTER_EXECUTABLE"][0].id,
            "noapache_requests_resource_id": self._noapache_requests,
            "run_mode": self._noapache_type,
            "check_responses_stability": self._noapache_type == "blender",
            "use_last_stable_grpc_client": self._grpc,
        })

        return defaults

    @property
    def attributes(self):
        parent = super(GetResponsesStandaloneNoapacheupperProdFlowDebug, self).attributes
        override = {
            "requirements": {
                "cores": 4,
                "ram": 64 * 1024 ** 3,
                "sandbox": {
                    "platform": "linux",
                    "priority": {
                        "class": "BACKGROUND",
                        "subclass": "LOW",
                    },
                },
            },
        }

        return CubeInput.update_recursive(
            parent,
            override
        )


class GetResponsesStandaloneNoapacheupperProdFlowDebugRelease(GetResponsesStandaloneNoapacheupperProdFlowDebug):  # TODO: add dependent compare test cube
    pass


class GetResponsesStandaloneBlenderGrpcUnistat(GetResponsesStandaloneNoapacheupperProdFlowDebug):  # TODO: add dependent compare test cube
    def __init__(self, build_noapacheupper_test, build_noapacheupper_data):
        super(GetResponsesStandaloneBlenderGrpcUnistat, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            noapache_type="blender",
            grpc=True,
            unistat=True,
            task="projects/upper_search/noapache/web_test_upper_unistat",
        )

    @property
    def input_override(self):
        return {
            "yasmcore_resource_id": resources.YASMCORE,
            "check_responses_stability": False,
            "requests_limit": 500,
            "workers_count": 2,
        }


class GetResponsesStandaloneNoapacheupperSan(GetApphostResponsesStandaloneNoapacheupper):
    def __init__(self, build_noapacheupper_test, build_noapacheupper_data, sanitizer):
        self._sanitizer = sanitizer

        super(GetResponsesStandaloneNoapacheupperSan, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            name="responses_standalone_{}san".format(sanitizer[0]),
            task="projects/upper_search/noapache/sanitize_upper",
        )

    @property
    def input_override(self):
        return {
            "sanitizer_type": self._sanitizer,
            "check_responses_stability": False,
        }

    @property
    def attributes(self):
        parent = super(GetResponsesStandaloneNoapacheupperSan, self).attributes
        override = {
            "requirements": {
                "cores": 4,
                "ram": 64 * 1024 ** 3,
                "sandbox": {
                    "platform": "linux",
                },
            },
        }

        return CubeInput.update_recursive(
            parent,
            override
        )
