# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_RETPATH,
    TEST_UID,
)
from passport.backend.core.builders.trust_api.faker import get_payment_methods_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants

from .base import (
    BaseStandaloneTestCase,
    TEST_ANTIFRAUD_EXTERNAL_ID,
    TEST_CARD_ID,
)


class StandaloneCreateTrackTestcase(BaseStandaloneTestCase):
    default_url = '/1/bundle/challenge/standalone/create_track/'
    http_query_args = {
        'antifraud_tags': json.dumps(['call', 'sms']),
        'antifraud_external_id': TEST_ANTIFRAUD_EXTERNAL_ID,
        'retpath': TEST_RETPATH,
        'uid': TEST_UID,
    }
    http_headers = {}

    def setUp(self):
        super(StandaloneCreateTrackTestcase, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={'challenge': ['standalone_create_track']}))

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.antifraud_tags, ['call', 'sms'])
        eq_(track.antifraud_external_id, TEST_ANTIFRAUD_EXTERNAL_ID)

    def test_3ds_ok(self):
        self.env.trust_payments.set_response_value(
            'get_payment_methods',
            get_payment_methods_response(),
        )
        resp = self.make_request(query_args=dict(card_id_for_3ds=TEST_CARD_ID))
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.antifraud_tags, ['call', 'sms'])
        eq_(track.antifraud_external_id, TEST_ANTIFRAUD_EXTERNAL_ID)
        eq_(track.paymethod_id, TEST_CARD_ID)

    def test_3ds_card_not_found(self):
        self.env.trust_payments.set_response_value(
            'get_payment_methods',
            get_payment_methods_response(),
        )
        resp = self.make_request(query_args=dict(card_id_for_3ds='card-xxx'))
        self.assert_error_response(resp, ['card_id.not_found'])
