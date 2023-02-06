# -*- coding: utf-8 -*-

import json
import time

from nose.tools import eq_
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    HEADERS,
    TEST_PHONE_NUMBER,
    TEST_UID,
)


@with_settings_hosts(
    YASMS_URL='http://localhost',
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    **mock_counters()
)
class TestMixedConfirm(BaseConfirmSubmitterTestCase, BaseConfirmCommitterTestCase):

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
            'uid': TEST_UID,
            'code': self.confirmation_code,
            'password': 'testpassword',
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def test_confirm_and_confirm_and_bind_secure_submits(self):
        c_rv = self.env.client.post(
            '/1/bundle/phone/confirm/submit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(c_rv.status_code, 200, c_rv.data)
        eq_(
            json.loads(c_rv.data),
            self.base_send_code_response,
        )

        cbs_rv = self.env.client.post(
            '/1/bundle/phone/confirm_and_bind_secure/submit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(cbs_rv.status_code, 200, cbs_rv.data)
        eq_(
            json.loads(cbs_rv.data),
            {
                u'status': u'error',
                u'errors': [u'track.invalid_state'],
                u'track_id': self.track_id,
            },
        )

    def test_confirm_submit_and_confirm_and_bind_secure_commit(self):
        c_rv = self.env.client.post(
            '/1/bundle/phone/confirm/submit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(c_rv.status_code, 200, c_rv.data)
        eq_(
            json.loads(c_rv.data),
            self.base_send_code_response,
        )

        cbs_rv = self.env.client.post(
            '/1/bundle/phone/confirm_and_bind_secure/commit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(cbs_rv.status_code, 200, cbs_rv.data)
        eq_(
            json.loads(cbs_rv.data),
            merge_dicts(
                self.number_response,
                {
                    u'status': u'error',
                    u'errors': [u'track.invalid_state'],
                },
            ),
        )

    def test_confirm_and_confirm_and_bind_secure_commits(self):
        # FIXME копипаста
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_code = self.confirmation_code
            track.phone_confirmation_sms = self.sms_text
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_first_send_at = time.time()
            track.phone_confirmation_last_send_at = time.time()
            track.phone_confirmation_method = 'by_sms'
            track.uid = TEST_UID
            track.state = 'confirm'

        c_rv = self.env.client.post(
            '/1/bundle/phone/confirm/commit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(c_rv.status_code, 200, c_rv.data)
        eq_(
            json.loads(c_rv.data),
            self.base_response,
        )

        cbs_rv = self.env.client.post(
            '/1/bundle/phone/confirm_and_bind_secure/commit/?consumer=dev',
            data=self.query_params(),
            headers=HEADERS,
        )

        eq_(cbs_rv.status_code, 200, cbs_rv.data)
        eq_(
            json.loads(cbs_rv.data),
            merge_dicts(
                self.number_response,
                {
                    u'status': u'error',
                    u'errors': [u'track.invalid_state'],
                },
            ),
        )
