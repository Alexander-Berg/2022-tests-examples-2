from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput


class TestSiteSearchIntegrationTestsCube(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestSiteSearchIntegrationTestsCube, self).__init__(
            name="test_sitesearch_integration_tests",
            ci_task_filename="web/sitesearch_integration_tests",
            needs=[beta_cube],
            attributes={
                "requirements": {
                    "sandbox": {
                        "platform": "linux_ubuntu_16.04_xenial",
                    },
                },
            },
        )

    @property
    def input_override(self):
        return {
            "serp_host": "{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
        }
