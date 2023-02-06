from datetime import datetime
from typing import List

from sandbox.projects.music.MusicDiffTest.lib.models.TestController import TestController


class TestRun:
    def __init__(self, component):
        self.title = datetime.now().strftime('%m.%d.%Y-%H:%M:%S') + f' TestRun for {component}'
        self.test_controllers: List[TestController] = []
        self.test_results = {}
        self.order = None
        self.build_number = ''

    def __str__(self):
        return_string = 'Testrun name: {}\n'.format(self.title)
        for test_controller in self.test_controllers:
            return_string += str(test_controller)
        return return_string

    def set_result_by_controller(self, controller_name: str,
                                 results: List[dict]):
        self.test_results[controller_name] = results

    def get_results(self):
        return self.test_results
