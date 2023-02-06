import unittest

from mock import MagicMock
from sandbox.projects.release_machine.client import RMClient


class TestRMClient(unittest.TestCase):

    def test_none_response_should_not_crash_the_client(self):
        test_component = "release_machine_test_tagged"
        client = RMClient()
        client._do_post = MagicMock(return_value=None)
        try:
            client.get_component(test_component)
            client.delete_component(test_component)
            client.get_components()
            client.get_scopes(test_component)
            client.get_state(test_component)
        except (TypeError, KeyError) as err:
            self.fail(u"None response should not result in a type or key error.\n{}".format(err.message))
