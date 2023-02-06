# -*- coding: utf-8 -*-
import logging

from nose.tools import eq_
from passport.backend.core.builders.trust_api import TrustTemporaryError
from passport.backend.core.builders.trust_api.faker import (
    cancel_payment_response,
    create_basket_response,
    get_basket_status_response,
    start_payment_response,
    TEST_3DS_URL,
    TEST_PAYMETHOD_ID,
    TEST_PURCHASE_TOKEN,
)
from passport.backend.core.builders.trust_api.trust_payments import (
    PAYMENT_RESP_CODE_NOT_ENOUGH_FUNDS,
    PAYMENT_STATUS_AUTHORIZED,
    PAYMENT_STATUS_NOT_AUTHORIZED,
    PAYMENT_STATUS_STARTED,
)
from passport.backend.core.conf import settings

from .base import (
    BaseTrust3DSTestCase,
    TEST_CARD_ID,
    TEST_LOGIN_ID,
    TEST_RETPATH,
    TEST_UID,
)


TEST_FRONTEND_URL = 'https://passport.yandex.ru/3ds'


log = logging.getLogger()


class Trust3DSSubmitTestCase(BaseTrust3DSTestCase):
    default_url = '/1/bundle/billing/3ds/verify/submit/?consumer=dev'
    http_query_args = {
        'frontend_url': TEST_FRONTEND_URL,
    }

    def setUp(self):
        super(Trust3DSSubmitTestCase, self).setUp()
        self.env.trust_payments.set_response_value(
            'create_basket',
            create_basket_response(),
        )
        self.env.trust_payments.set_response_value(
            'start_payment',
            start_payment_response(uid=TEST_UID),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.paymethod_id = TEST_PAYMETHOD_ID
            track.uid = str(TEST_UID)
            track.retpath = TEST_RETPATH
            track.antifraud_tags = ['3ds', 'call', 'sms']

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            status='ok',
        )
        self.assert_statbox_log(status='ok', with_check_cookies=True)

        self.env.trust_payments.get_requests_by_method('create_basket')[0].assert_properties_equal(
            json_data={
                'paymethod_id': TEST_PAYMETHOD_ID,
                'product_id': settings.TRUST_3DS_CHALLENGE_PRODUCT_ID,
                'amount': 11,
                'currency': 'RUB',
                'return_path': TEST_FRONTEND_URL,
                'afs_params': {
                    'login_id': TEST_LOGIN_ID,
                    'chaas': True,
                },
                'pass_params': {
                    'terminal_route_data': {
                        'service_force_3ds': 1,
                    },
                },
                'template_tag': 'desktop/form',
            },
        )

        track = self.track_manager.read(self.track_id)

        eq_(
            track.purchase_token,
            TEST_PURCHASE_TOKEN,
        )
        eq_(len(self.env.trust_payments.requests), 2)

    def test_ok_with_custom_params(self):
        rv = self.make_request(query_args=dict(use_new_trust_form=True, use_mobile_layout=True))

        self.assert_ok_response(
            rv,
            status='ok',
        )
        self.assert_statbox_log(status='ok', with_check_cookies=True)

        self.env.trust_payments.get_requests_by_method('create_basket')[0].assert_properties_equal(
            json_data={
                'product_id': settings.TRUST_3DS_CHALLENGE_PRODUCT_ID,
                'amount': 11,
                'currency': 'RUB',
                'return_path': TEST_FRONTEND_URL,
                'afs_params': {
                    'login_id': TEST_LOGIN_ID,
                    'chaas': True,
                },
                'pass_params': {
                    'terminal_route_data': {
                        'service_force_3ds': 1,
                    },
                },
                'template_tag': 'mobile/form',
                'developer_payload': '{"selected_card_id": "%s", "blocks_visibility": {"cardSelector": false}, "auto_start_payment": true, "template": "checkout"}' % TEST_PAYMETHOD_ID,
            },
        )

        track = self.track_manager.read(self.track_id)

        eq_(
            track.purchase_token,
            TEST_PURCHASE_TOKEN,
        )
        eq_(len(self.env.trust_payments.requests), 2)

    def test_invalid_track_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.paymethod_id = None

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
        )


class Trust3DSCommitTestCase(BaseTrust3DSTestCase):
    default_url = '/1/bundle/billing/3ds/verify/commit/?consumer=dev'

    def setUp(self):
        super(Trust3DSCommitTestCase, self).setUp()
        self.env.trust_payments.set_response_value(
            'get_basket_status',
            get_basket_status_response(uid=TEST_UID, payment_status=PAYMENT_STATUS_AUTHORIZED),
        )
        self.env.trust_payments.set_response_value(
            'cancel_payment',
            cancel_payment_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.paymethod_id = TEST_CARD_ID
            track.uid = str(TEST_UID)
            track.retpath = TEST_RETPATH
            track.purchase_token = TEST_PURCHASE_TOKEN

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            status='ok',
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_AUTHORIZED,
            with_check_cookies=True,
        )

        track = self.track_manager.read(self.track_id)
        eq_(
            track.payment_status,
            PAYMENT_STATUS_AUTHORIZED,
        )

    def test_failed_to_cancel_payment(self):
        self.env.trust_payments.set_response_side_effect(
            'cancel_payment',
            TrustTemporaryError(),
        )
        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['backend.trust_bindings_failed'],
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_AUTHORIZED,
            with_check_cookies=True,
        )

        track = self.track_manager.read(self.track_id)
        eq_(
            track.payment_status,
            None,
        )

    def test_3ds_not_passed(self):
        self.env.trust_payments.set_response_value(
            'get_basket_status',
            get_basket_status_response(uid=TEST_UID, payment_status=PAYMENT_STATUS_STARTED, with_3ds_url=True),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['3ds.not_passed'],
            url_3ds=TEST_3DS_URL,
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_STARTED,
            with_check_cookies=True,
        )

    def test_3ds_not_passed_with_new_form(self):
        self.env.trust_payments.set_response_value(
            'get_basket_status',
            get_basket_status_response(
                uid=TEST_UID,
                payment_status=PAYMENT_STATUS_STARTED,
                with_3ds_url=True,
                use_new_trust_form=True,
            ),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['3ds.not_passed'],
            url_3ds=TEST_3DS_URL,
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_STARTED,
            with_check_cookies=True,
        )

    def test_3ds_failed(self):
        self.env.trust_payments.set_response_value(
            'get_basket_status',
            get_basket_status_response(
                uid=TEST_UID,
                payment_status=PAYMENT_STATUS_NOT_AUTHORIZED,
                payment_resp_code='unknown_reason',
            ),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['3ds.failed'],
            payment_status=PAYMENT_STATUS_NOT_AUTHORIZED,
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_NOT_AUTHORIZED,
            with_check_cookies=True,
        )

    def test_3ds_not_enough_funds(self):
        self.env.trust_payments.set_response_value(
            'get_basket_status',
            get_basket_status_response(
                uid=TEST_UID,
                payment_status=PAYMENT_STATUS_NOT_AUTHORIZED,
                payment_resp_code=PAYMENT_RESP_CODE_NOT_ENOUGH_FUNDS,
            ),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['3ds.not_enough_funds'],
            payment_status=PAYMENT_STATUS_NOT_AUTHORIZED,
        )
        self.assert_statbox_log(
            mode='3ds_verify_status',
            status=PAYMENT_STATUS_NOT_AUTHORIZED,
            with_check_cookies=True,
        )

    def test_invalid_track_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.purchase_token = None

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
        )
