from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput
from sandbox.projects.release_machine.core import const as rm_const


class TestXMLTestsCube(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestXMLTestsCube, self).__init__(
            name="test_xml_tests",
            ci_task_filename="web/xml_tests",
            needs=[beta_cube],
        )

    @property
    def input_defaults(self):
        defaults = super(TestXMLTestsCube, self).input_defaults
        defaults.update({
            "beta_url": "https://{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
            "diff_barrier": 0.05,  # 5 percent diff
            "shoots_number": 150,
            "queries_plan": 135625826,
            "component_name": self._beta_cube.component_name,
            "release_number": rm_const.CIJMESPathCommon.MAJOR_RELEASE_NUM,
        })

        return defaults
