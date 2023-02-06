from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.noapache.noapache_tests.get_responses import GetResponsesStandaloneNoapacheupperDebug


class ExtremeTestsStandaloneNoapacheupperDebug(GetResponsesStandaloneNoapacheupperDebug):
    """
        Few noapache runs with config options which cause problems earlier (obviuosly segfault/busyloop)
    """
    def __init__(self, build_noapacheupper_test, build_noapacheupper_data, test_type):
        super(ExtremeTestsStandaloneNoapacheupperDebug, self).__init__(
            build_noapacheupper_test,
            build_noapacheupper_data,
            test_type,
            name="kubr_extreme_standalone_upper_debug",
            task="projects/upper_search/noapache/extreme_standalone_noapacheupper2",
        )
