from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube, CubeInput


class TestEmptyExperimet(Cube):
    def __init__(self, build_noapacheupper, build_noapacheupper_rearrange, web_beta):
        self._build_noapacheupper = build_noapacheupper
        self._build_noapacheupper_rearrange = build_noapacheupper_rearrange
        self._beta = web_beta

        super(TestEmptyExperimet, self).__init__(
            name="test_empty_experiment",
            task="projects/upper_search/noapache/get_standalone_eventlog",
            needs=[build_noapacheupper, build_noapacheupper_rearrange, web_beta],
        )

    @property
    def input_defaults(self):
        return {
            "executable": self._build_noapacheupper.output.resources["NOAPACHE_UPPER"][0].id,
            "rearrange_data": self._build_noapacheupper_rearrange.output.resources["REARRANGE_DATA"][0].id,
            "config_source": "{}.ru".format(CubeInput.format_cube_output_value(self._beta.output_params.new_beta_url)),
            "new_cgi_param": "",
            "scraper_pool": "upper_web_priemka",
            "component_name": self._beta.component_name,
        }
