# coding: utf-8
from time import time
import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.messenger_api import (
    BaseMessengerApiError,
    get_mssngr_fanout_api,
    MessengerApiPermanentError,
    MessengerApiTemporaryError,
)
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import (
    FakeMessengerAPI,
    messenger_api_empty_response,
    messenger_api_error_response,
    messenger_api_html_response,
    messenger_api_invalid_response_another_message_type,
    messenger_api_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_UID = 12345


@with_settings(
    MESSENGER_FANOUT_API_URL='http://localhost/',
    MESSENGER_FANOUT_API_TIMEOUT=1,
    MESSENGER_FANOUT_API_RETRIES=2,
)
class TestMssngrFanoutAPICommon(unittest.TestCase):
    def setUp(self):
        self.fake_messenger_api = FakeMessengerAPI()
        self.fake_messenger_api.start()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'messenger_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

        self.messenger_api = get_mssngr_fanout_api()

    def tearDown(self):
        del self.messenger_api
        self.fake_messenger_api.stop()
        del self.fake_messenger_api
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_ok(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID, time() - 5))
        eq_(
            self.messenger_api.check_user_lastseen(TEST_UID),
            5,
        )

    def test_in_future_ok(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID, time() + 5))
        eq_(
            self.messenger_api.check_user_lastseen(TEST_UID),
            0,
        )

    def test_no_messenger_ok(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', messenger_api_empty_response())
        eq_(
            self.messenger_api.check_user_lastseen(TEST_UID),
            -1,
        )

    def test_error(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', messenger_api_error_response())
        with assert_raises(BaseMessengerApiError):
            self.messenger_api.check_user_lastseen(TEST_UID)

    def test_bad_request(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', messenger_api_error_response('Invalid request'), status=400)
        with assert_raises(MessengerApiPermanentError):
            self.messenger_api.check_user_lastseen(TEST_UID)

    def test_unusual_status(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', '', status=418)
        with assert_raises(MessengerApiPermanentError):
            self.messenger_api.check_user_lastseen(TEST_UID)

    def test_temporary(self):
        self.fake_messenger_api.set_response_value('check_user_lastseen', '', status=503)
        with assert_raises(MessengerApiTemporaryError):
            self.messenger_api.check_user_lastseen(TEST_UID)

    @parameterized.expand([
        (messenger_api_html_response,),
        (messenger_api_invalid_response_another_message_type,),
    ])
    def test_parser_error(self, response):
        self.fake_messenger_api.set_response_value('check_user_lastseen', response)
        with assert_raises(MessengerApiPermanentError):
            self.messenger_api.check_user_lastseen(TEST_UID)
