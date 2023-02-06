# -*- coding: utf-8 -*-

from datetime import datetime

from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1 as TEST_PHONE_NUMBER_EXTRA,
    TEST_PORTAL_ALIAS_TYPE,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.models.phones.faker import build_current_phone_binding
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import datetime_to_integer_unixtime

from .base import PhoneManageBaseTestCase
from .base_test_data import (
    TEST_PHONE_BOUND_DT,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_ID,
    TEST_PHONE_ID_EXTRA,
)


class TestSecurifySudo(PhoneManageBaseTestCase):
    base_method_path = '/1/bundle/phone/manage/securify/sudo/'
    base_request_args = {'phone_id': TEST_PHONE_ID, 'uid': TEST_UID}

    def setUp(self):
        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
            'bound': TEST_PHONE_BOUND_DT,
            'confirmed': TEST_PHONE_BOUND_DT,
        }
        self.phone_binding = build_current_phone_binding(
            TEST_PHONE_ID,
            TEST_PHONE_NUMBER.e164,
            TEST_PHONE_BOUND_DT,
        )
        super(TestSecurifySudo, self).setUp()

    def set_blackbox_response(
        self,
        account_attributes=None,
        phones=None,
        operations=None,
        phone_bindings=None,
    ):
        password_is_set = True
        phones=phones if phones is not None else [self.phone]
        phone_bindings=phone_bindings if phone_bindings is not None else [self.phone_binding]

        alias_kwargs = {
            'aliases': {
                TEST_PORTAL_ALIAS_TYPE: TEST_LOGIN,
            },
        }

        bb_kwargs = merge_dicts(
            {
                'login': TEST_LOGIN,
                'phones': phones,
                'phone_operations': operations,
                'attributes': account_attributes,
                'crypt_password': '1:pass' if password_is_set else None,
                'phone_bindings': phone_bindings,
            },
            alias_kwargs,
        )
        bb_response = blackbox_sessionid_multi_response(
            have_password=password_is_set,
            **bb_kwargs
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )

        self.env.db.serialize(bb_response)

    def test_ok(self):
        self.set_blackbox_response()
        rv = self.make_request()
        assert rv.status_code == 200
        self.assert_ok_response(rv)

        self.check_db_phone_attr('number', TEST_PHONE_NUMBER.digital)
        self.check_db_phone_attr('created', str(datetime_to_integer_unixtime(self.phone['created'])))
        self.check_db_phone_attr('bound', str(datetime_to_integer_unixtime(self.phone['bound'])))
        self.check_db_phone_attr('secured', TimeNow())
        self.env.db.check('attributes', 'phones.secure', str(TEST_PHONE_ID), uid=TEST_UID, db='passportdbshard1')

        self.env.event_logger.assert_events_are_logged({
            'consumer': 'dev',
            'action': 'securify_sudo',
            'phone.1.action': 'changed',
            'phone.1.number': TEST_PHONE_NUMBER.e164,
            'phone.1.secured': TimeNow(),
            'phones.secure': '1',
            'user_agent': 'curl',
        })

    def test_has_secure(self):
        assert TEST_PHONE_NUMBER_EXTRA != TEST_PHONE_NUMBER
        self.set_blackbox_response(
            account_attributes={
                'phones.secure': TEST_PHONE_ID_EXTRA,
            },
            phones=[
                {
                    'number': TEST_PHONE_NUMBER.e164,
                    'id': TEST_PHONE_ID,
                    'created': TEST_PHONE_CREATED_DT,
                    'bound': TEST_PHONE_BOUND_DT,
                    'confirmed': TEST_PHONE_BOUND_DT,
                },
                {
                    'number': TEST_PHONE_NUMBER_EXTRA.e164,
                    'id': TEST_PHONE_ID_EXTRA,
                    'created': TEST_PHONE_CREATED_DT,
                    'bound': TEST_PHONE_BOUND_DT,
                    'confirmed': TEST_PHONE_BOUND_DT,
                    'secured': datetime.now(),
                },
            ]
        )
        rv = self.make_request()
        assert rv.status_code == 200
        self.assert_error_response(rv, ['action.impossible'])

    def test_has_secure_op(self):
        self.set_blackbox_response(
            account_attributes={
                'phones.secure': '1',
            },
            operations=[{
                'id': 100,
                'phone_id': 1,
                'type': 'bind',
                'security_identity': int(TEST_PHONE_NUMBER),
            }]
        )
        rv = self.make_request()
        assert rv.status_code == 200
        self.assert_error_response(rv, ['action.impossible'])

    def test_number_unbound(self):
        phone = dict(self.phone)
        del phone['bound']
        phone_binding = dict(self.phone_binding)
        del phone_binding['bound']
        self.set_blackbox_response(
            phones=[phone],
            phone_bindings=[phone_binding],
        )
        rv = self.make_request()
        assert rv.status_code == 200
        self.assert_error_response(rv, ['action.impossible'])

    def test_phone_not_found(self):
        self.set_blackbox_response(
            phones=[],
            phone_bindings=[],
        )
        rv = self.make_request()
        assert rv.status_code == 200
        self.assert_error_response(rv, ['phone.not_found'])
