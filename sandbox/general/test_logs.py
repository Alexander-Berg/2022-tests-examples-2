from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base import SearchReleasesBetaTestCube
from sandbox.projects.release_machine.components.config_core.jg.cube.base import CubeInput


class TestLogs(SearchReleasesBetaTestCube):
    def __init__(self, beta_cube):
        """
        :type beta_cube: yappy.GenerateYappyBeta
        :param beta_cube:
            The beta cube this cube depends on
        """

        self._beta_cube = beta_cube

        super(TestLogs, self).__init__(
            name="test_logs",
            ci_task_filename="test_logs",
            needs=[beta_cube],
        )

    @property
    def input_defaults(self):
        defaults = super(TestLogs, self).input_defaults
        defaults.update({
            "trunk_beta_url": "https://hamster.yandex.ru",
            "branch_beta_url": "https://{}.ru".format(CubeInput.format_cube_output_value(self._beta_cube.output_params.new_beta_url)),
            "yt_token_secret_name": "yt_token",
            "yt_token_secret_id": "sec-01g02dcjabbha085e83qvcxggm",
            "yt_pool": "sessions-experiments-a",
            "yt_prefix_path": "//home/userdata-dev/zsafiullin/upper",
        })

        return defaults
