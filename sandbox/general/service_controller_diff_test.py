from sandbox.projects.release_machine.components.config_core.jg.cube.lib.infra import InfraDiffTestCube


class ServiceControllerDiffTest(InfraDiffTestCube):
    def __init__(self, build_cube):
        """
        :type build_cube: Cube
        :param build_cube:
            Build cube to run test
        """

        self._build_cube = build_cube

        super(ServiceControllerDiffTest, self).__init__(
            name="service_controller_diff_test",
            title="SERVICE_CONTROLLER_DIFF_TEST",
            ci_task_filename="service_controller/service_controller_diff_test",
            needs=[build_cube],
        )

    @property
    def input_defaults(self):
        return {
            "service_controller_testing_binary": self._build_cube.output.resources["SERVICE_CONTROLLER_BINARY"][0].id
        }
