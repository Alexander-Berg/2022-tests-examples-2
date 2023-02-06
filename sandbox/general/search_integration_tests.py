from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.common import constants as sandbox_constants
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput


class TestSearchIntegrationSoyHttpTestsCube(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube, soy_pool):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on

        :type soy_pool: str
        :param soy_pool:
            The name of the soy_pool
        """

        self._beta_cube = beta_cube
        self._soy_pool = soy_pool

        super(TestSearchIntegrationSoyHttpTestsCube, self).__init__(
            name="test_search_integration_soy_http_tests",
            ci_task_filename="web/search_integration_tests",
            needs=[beta_cube],
        )

    @property
    def env_vars(self):
        return {
            "BETA_HOST": "{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
            "SOY_MODE": 1,
            "SOY_MAP_OP_TYPE": "http",
            "OAUTH_TOKEN": "'$(vault:value:SEARCH-RELEASERS:common_release_token)'",
            "SOY_POOL": self._soy_pool,
        }

    @property
    def input_override(self):
        return {
            "targets": "search/integration_tests",
            sandbox_constants.DISABLE_TEST_TIMEOUT: True,
            sandbox_constants.YA_MAKE_EXTRA_PARAMETERS: ["--test-filter=mark:soy_http", "--test-stderr"],
            sandbox_constants.ENV_VARS: " ".join(["{}={}".format(k, v) for k, v in self.env_vars.items()]),
            "retry_task": 3,
            "threshold_failed_tests": 100,
            "retry_all_tests": True,
            sandbox_constants.TESTS_REQUESTED: True,
            sandbox_constants.BUILD_SYSTEM_KEY: sandbox_constants.YMAKE_BUILD_SYSTEM,
            sandbox_constants.ALLOW_AAPI_FALLBACK: True,
            sandbox_constants.USE_AAPI_FUSE: True,
            sandbox_constants.USE_ARC_INSTEAD_OF_AAPI: False,
        }


class TestSearchIntegrationTestsCube(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube, soy_pool):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on

        :type soy_pool: str
        :param soy_pool:
            The name of the soy_pool
        """

        self._beta_cube = beta_cube
        self._soy_pool = soy_pool

        super(TestSearchIntegrationTestsCube, self).__init__(
            name="test_search_integration_tests",
            ci_task_filename="web/search_integration_tests",
            needs=[beta_cube],
        )

    @property
    def env_vars(self):
        return {
            "BETA_HOST": "{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
            "SOY_MODE": 1,
            "SOY_MAP_OP_TYPE": "scraper",
            "OAUTH_TOKEN": "'$(vault:value:SEARCH-RELEASERS:common_release_token)'",
            "SOY_POOL": self._soy_pool,
        }

    @property
    def input_override(self):
        return {
            "targets": "search/integration_tests",
            sandbox_constants.DISABLE_TEST_TIMEOUT: True,
            sandbox_constants.YA_MAKE_EXTRA_PARAMETERS: ["--test-filter=mark:not soy_http", "--test-stderr"],
            sandbox_constants.ENV_VARS: " ".join(["{}={}".format(k, v) for k, v in self.env_vars.items()]),
            "retry_task": 3,
            "threshold_failed_tests": 100,
            "retry_all_tests": True,
            sandbox_constants.TESTS_REQUESTED: True,
            sandbox_constants.BUILD_SYSTEM_KEY: sandbox_constants.YMAKE_BUILD_SYSTEM,
            sandbox_constants.ALLOW_AAPI_FALLBACK: True,
            sandbox_constants.USE_AAPI_FUSE: True,
            sandbox_constants.USE_ARC_INSTEAD_OF_AAPI: False,
        }
