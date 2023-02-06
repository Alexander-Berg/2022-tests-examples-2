from sandbox.projects.release_machine.components.config_core.jg.cube.lib.upper_search.base.web import TestXMLTestsCube


class TestXMLTests(TestXMLTestsCube):
    @property
    def input_override(self):
        return {
            "shoots_number": 50,
            "validate_beta": True,
            "add_cgi": "&numdoc=10",
        }
