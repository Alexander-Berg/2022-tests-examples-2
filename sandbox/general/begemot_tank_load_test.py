from sandbox.projects.release_machine.components.config_core.jg.cube import Cube


class BegemotTankLoadTest(Cube):
    def __init__(self, name, title, input):
        super(self.__class__, self).__init__(
            name=name,
            title=title,
            task="projects/begemot/tasks/begemot_tank_load_test",
            input=input,
        )
