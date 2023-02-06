from unittest import TestCase

from passport.backend.core.logging_utils.request_id import RequestIdManager
from passport.backend.logbroker_client.core.utils import LogPrefixManager


class LogPrefixManagerTestCase(TestCase):
    def test_system_context(self):
        assert RequestIdManager.get_request_id() == ''
        with LogPrefixManager.system_context('some_id', 'other_id'):
            assert RequestIdManager.get_request_id() == '@some_id,other_id'
        assert RequestIdManager.get_request_id() == ''

    def test_user_context(self):
        assert RequestIdManager.get_request_id() == ''

        with LogPrefixManager.system_context('some_value', 'other_value'):
            assert RequestIdManager.get_request_id() == '@some_value,other_value'

            with LogPrefixManager.user_context('some_user_value', 'other_user_value'):
                assert RequestIdManager.get_request_id() == '@some_value,other_value,some_user_value,other_user_value'

            assert RequestIdManager.get_request_id() == '@some_value,other_value'

        assert RequestIdManager.get_request_id() == ''
