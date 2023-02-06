from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base.video import TestE2ETestsVideo


class TestE2ETestsVideoFP(TestE2ETestsVideo):
    def __init__(self, beta_cube, **kwargs):
        super(TestE2ETestsVideoFP, self).__init__(beta_cube, **kwargs)

    @property
    def input_override(self):
        return {
            "platforms": ["desktop", "touch-pad", "touch-phone", "tv"],
        }
