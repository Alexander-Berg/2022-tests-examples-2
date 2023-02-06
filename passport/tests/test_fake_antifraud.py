# -*- coding: utf-8 -*-
from unittest import TestCase

from passport.backend.core.builders.antifraud import (
    AntifraudApi,
    AntifraudApiInvalidResponse,
    AntifraudApiTemporaryError,
    ScoreAction,
    ScoreResponse,
    UIDCardsResponse,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import FakeAntifraudAPI
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


@with_settings(
    ANTIFRAUD_API_URL='http://localhost',
    ANTIFRAUD_API_TIMEOUT=2,
    ANTIFRAUD_API_RETRIES=1,
)
class FakeYsaMirrorTestCase(TestCase):
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

        self.fake_af = FakeAntifraudAPI()
        self.fake_af.start()
        self.af = AntifraudApi()

    def tearDown(self):
        self.fake_af.stop()
        del self.fake_af
        self.fake_tvm.stop()
        del self.fake_tvm

    def test_mock_result(self):
        self.fake_af.set_response_value_without_method({
            'status': 'success',
            'action': 'ALLOW',
            'reason': 'reason',
            'tags': [],
        })
        assert self.af.score({'key': 'value'}) == ScoreResponse(
            action=ScoreAction.ALLOW,
            reason='reason',
            tags=[],
        )

    def test_mock_cards(self):
        self.fake_af.set_response_value(
            'uid_cards',
            {
                'status': 'success',
                'action': 'ALLOW',
                'reason': 'reason',
                'tags': [],
                'verified_cards_per_uid': {
                    '1': {'key': 5},
                    '2': {'key': 6},
                    '3': {},
                },
            },
        )
        assert self.af.uid_cards(uids=[1, 2, 3]) == UIDCardsResponse(
            action=ScoreAction.ALLOW,
            reason='reason',
            tags=[],
            uids_with_cards={1: True, 2: True, 3: False},
        )

    def test_mock_error(self):
        self.fake_af.set_response_side_effect_without_method(AntifraudApiTemporaryError)
        self.assertRaises(AntifraudApiTemporaryError, self.af.score, {'key': 'value'})

    def test_parse_error(self):
        self.fake_af.set_response_value_without_method(b'bad json')
        self.assertRaises(AntifraudApiInvalidResponse, self.af.score, {'key': 'value'})
