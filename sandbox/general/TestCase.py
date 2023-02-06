from typing import List

from sandbox.projects.music.MusicDiffTest.lib.models.TestStep import TestStep


class TestCase:
    def __init__(self, id, title, description, users):
        self.title = title
        self.description = description
        self.test_steps: List[TestStep] = []
        self.id = id
        self.shared_data = {
            "host1": {},
            "host2": {}
        }
        self.users = users

    def __str__(self):
        return_string = (f'TestCase #{self.id}: '
                         f'{self.title}\n{self.description}\n')
        for step in self.test_steps:
            return_string += str(step)
        return return_string
