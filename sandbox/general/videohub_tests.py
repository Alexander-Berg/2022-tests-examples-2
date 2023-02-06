from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput


class TestVideohubTestsCube(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestVideohubTestsCube, self).__init__(
            name="test_videohub_tests",
            ci_task_filename="video/videohub_tests",
            needs=[beta_cube],
        )

    @property
    def input_override(self):
        return {
            "beta_url": "https://{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
        }
