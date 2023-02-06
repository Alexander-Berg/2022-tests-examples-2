from sandbox.projects.release_machine.components.config_core.jg.cube.lib import internal


class ConfigureAbExperimentsTests(internal.ReleaseMachineInternalTaskletCube):
    """release_machine/tasklets/ab_tests/configure_ab_experiments_tests"""

    TASK = "projects/release_machine/configure_ab_experiments_tests"
    TYPE = "configure"

    def __init__(self, component_name, testid_commit, **kwargs):
        self._testid_commit = testid_commit
        super(ConfigureAbExperimentsTests, self).__init__(component_name=component_name, **kwargs)

    @property
    def input_override(self):
        return {
            "config": {
                "ab_config_input": {
                    "testid_commit": self._testid_commit,
                },
            },
        }


class AbExperimentsApprovementCreator(internal.ReleaseMachineInternalCube):
    TASK = "projects/release_machine/ab_experiments_approvement_creator"
