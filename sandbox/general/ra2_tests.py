from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput


class TestRA2Tests(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestRA2Tests, self).__init__(
            name="test_ra2_tests",
            ci_task_filename="web/ra2_tests",
            needs=[beta_cube],
        )

    @property
    def input_override(self):
        return {
            "checked_beta": CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url),
            "launch_tdi": False,
            "launch_RA_for_blender_and_video": False,
            "launch_new_RA_for_blender_and_video": True,
            "launch_personalization_RA2": True,
            "launch_new_RA": True,
            "launch_images_RA": True,
            "launch_video_RA": True,
            "launch_videoserp_RA": True,
            "launch_new_RA_for_people": True,
            "launch_new_RA_for_people_wizard": True,
            "launch_new_RA_for_people_vertical": True,
            "seek_queries": True,
            "seek_two_contexts_features_diff_binary": True,
            "sample_beta": "hamster",
            "ignore_passed": True,
        }
