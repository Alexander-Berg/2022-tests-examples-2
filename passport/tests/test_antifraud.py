# -*- coding: utf-8 -*-
import json

from nose.tools import assert_raises
from passport.backend.core.builders.antifraud import (
    AntifraudApi,
    AntifraudApiTemporaryError,
    ScoreAction,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    antifraud_verified_cards_per_uid_response,
    FakeAntifraudAPI,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.useragent.faker.useragent import (
    FakedTimeoutError,
    UserAgentFaker,
)


MOBILEPROXY_INTERNAL_HOST = 'mobileproxy-internal.passport.yandex.net'


@with_settings(
    ANTIFRAUD_API_URL='http://localhost',
    ANTIFRAUD_API_TIMEOUT=2,
    ANTIFRAUD_API_RETRIES=1,
)
class TestAntifraudApi(PassportTestCase):
    def setUp(self):
        self.fake_af = FakeAntifraudAPI()
        self.fake_af.start()
        self.fake_af.set_response_value('score', antifraud_score_response())
        self.fake_af.set_response_value('save', antifraud_score_response())
        self.fake_af.set_response_value('uid_cards', antifraud_verified_cards_per_uid_response([]))
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'antifraud_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()

    def tearDown(self):
        self.fake_tvm.stop()
        self.fake_af.stop()
        del self.fake_tvm
        del self.fake_af

    def test_score(self):
        client = AntifraudApi()
        response = client.score({'key': 'value'})
        assert response.action == ScoreAction.ALLOW
        assert response.reason == 'some-reason'
        assert response.tags == []
        assert len(self.fake_af.requests) == 1
        request = self.fake_af.requests[0]
        assert request.post_args == json.dumps({'key': 'value'})
        assert 'X-Request-Deadline' in request._headers
        assert request._headers['X-Request-Deadline'] == TimeNow(as_milliseconds=True)

    def test_save(self):
        client = AntifraudApi()
        client.save({'key': 'value'})
        assert len(self.fake_af.requests) == 1
        request = self.fake_af.requests[0]
        assert request.post_args == json.dumps({'key': 'value'})

    def test_uid_cards(self):
        client = AntifraudApi()
        response = client.uid_cards([1, 2, 3])
        assert len(self.fake_af.requests) == 1
        request = self.fake_af.requests[0]
        assert request.post_args == json.dumps({'uids': ['1', '2', '3']})

        assert 'X-Request-Deadline' in request._headers
        assert request._headers['X-Request-Deadline'] == TimeNow(as_milliseconds=True)

        assert response.action == ScoreAction.ALLOW
        assert response.reason == ''
        assert response.tags == []
        assert response.uids_with_cards == dict()


@with_settings(
    ANTIFRAUD_API_URL='http://localhost',
    ANTIFRAUD_API_TIMEOUT=2,
    ANTIFRAUD_API_RETRIES=1,
)
class TestAntifraudCommon(PassportTestCase):
    def setUp(self):
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'antifraud_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()
        self.user_agent_faker = UserAgentFaker()
        self.user_agent_faker.start()

    def tearDown(self):
        self.user_agent_faker.stop()
        self.fake_tvm.stop()

        del self.user_agent_faker
        del self.fake_tvm

    def test_timeout(self):
        self.user_agent_faker.set_responses([
            FakedTimeoutError(),
        ])

        client = AntifraudApi()
        with assert_raises(AntifraudApiTemporaryError):
            client.score({'key': 'value'})
