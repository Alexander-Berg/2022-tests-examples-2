from sandbox.projects.release_machine.components.config_core.jg.cube.base import Cube
from sandbox.projects.release_machine.components.config_core.jg.cube.lib.internal import TYPE_TEST


class GetBegemotResponsesTest(Cube):
    TYPE = TYPE_TEST
    NOT_REQUIRED_BY_RELEASE = True

    def __init__(self, build_cube, request_plan, **kwargs):
        """
        :type build_cube: Cube
        :param build_cube:
            Build cube for test's dependencies

        :type request_plan: int
        :param request_plan:
            Input param for GET_BEGEMOT_RESPONSES task
        """

        self._build_cube = build_cube
        self._request_plan = request_plan

        super(GetBegemotResponsesTest, self).__init__(
            name="get_begemot_responses_test",
            task="projects/upper_search/request_init/get_begemot_responses",
            needs=[build_cube],
            **kwargs
        )

    @property
    def input_defaults(self):
        return {
            "begemot_binary": self._build_cube.output.resources["BEGEMOT_REQUEST_INIT_EXECUTABLE"][0].id,
            "fast_build_config": self._build_cube.output.resources["BEGEMOT_FAST_BUILD_CONFIG_REQUEST_INIT"][0].id,
            "request_plan": self._request_plan,
        }


class CheckBegemotResponsesTest(Cube):
    TYPE = TYPE_TEST

    def __init__(self, get_reponses_cube, build_cube, request_plan, **kwargs):
        """
        :type get_reponses_cube: Cube
        :param get_reponses_cube:
            GET_BEGEMOT_RESPONSES tests cube for dependencies

        :type build_cube: Cube
        :param build_cube:
            Build cube for input resource

        :type request_plan: int
        :param request_plan:
            Input param from GET_BEGEMOT_RESPONSES task
        """

        self._get_reponses_cube = get_reponses_cube
        self._build_cube = build_cube
        self._request_plan = request_plan

        super(CheckBegemotResponsesTest, self).__init__(
            name="check_begemot_responses_test",
            task="projects/upper_search/request_init/check_begemot_responses",
            needs=[get_reponses_cube],
            **kwargs
        )

    @property
    def input_defaults(self):
        return {
            "begemot_eventlog": self._get_reponses_cube.output.resources["BEGEMOT_EVENTLOG"][0].id,
            "evlogdump": self._build_cube.output.resources["BEGEMOT_EVLOGDUMP"][0].id,
            "queries": self._request_plan,
        }
