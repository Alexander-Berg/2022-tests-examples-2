from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput
from sandbox.projects.release_machine.core import const as rm_const


class TestE2ETestsWeb(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube, **kwargs):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestE2ETestsWeb, self).__init__(
            name="test_e2e_tests_web",
            ci_task_filename="web/e2e_tests_web",
            needs=[beta_cube],
            **kwargs
        )

    @property
    def input_override(self):
        return {
            "hermionee2e_base_url": "https://{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
            "test_id": 1,
            "allow_data_flags": False,
            "tests_block": None,
            "release": "latest",
            "project_git_base_ref": None,
            "tests_source": "nothing",
            "tests_hash": None,
            "tools": ["hermione-e2e"],
            "platforms": ["desktop", "touch-pad", "touch-phone"],
            "component_name": self._beta_cube.component_name,
            "release_number": rm_const.CIJMESPathCommon.MAJOR_RELEASE_NUM,
            "release_machine_mode": True,
        }
