# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_DISPLAY_LANGUAGE,
    TEST_OPERATION_ID,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.ufo_api.faker import ufo_api_phones_stats_response
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_PHONE_TYPE,
    EXTENDED_ATTRIBUTES_TYPE_TO_NAME_MAPPING,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import zero_datetime

from .base import PhoneManageBaseTestCase
from .base_test_data import (
    TEST_PASSWORD,
    TEST_PHONE_BOUND_DT,
    TEST_PHONE_ID,
)


phone_attr_ttn = EXTENDED_ATTRIBUTES_TYPE_TO_NAME_MAPPING[EXTENDED_ATTRIBUTES_PHONE_TYPE]


class BaseIntegrationalTestCase(PhoneManageBaseTestCase):

    def setUp(self):
        super(BaseIntegrationalTestCase, self).setUp()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE_NUMBER),
        )

    def get_operation_dict_from_db(self, operation_id=TEST_OPERATION_ID):
        data = self.env.db.get(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID,
            id=operation_id,
        )
        return dict(data)

    def set_actual_blackbox_response(self, **bb_kwargs):
        """
        Делаем ответ ЧЯ, соответствующий текущему состоянию БД,
        то есть все телефоны и операции читаем из БД и добавляем в ответ ЧЯ их и только их.
        """

        # Подготовим телефоны
        phones_data = self.env.db.select(
            'extended_attributes',
            entity_type=EXTENDED_ATTRIBUTES_PHONE_TYPE,
            uid=TEST_UID,
            db='passportdbshard1',
        )
        phones_data = map(dict, phones_data)

        phones = {}
        for phone in phones_data:
            phone_id = phone['entity_id']
            ext_attr_type = phone['type']

            if phone_id not in phones:
                phones[phone_id] = {'id': phone_id}

            phones[phone_id][phone_attr_ttn[ext_attr_type]] = str(phone['value'])

        phones = phones.values()
        for phone in phones:
            number = phone.get('number')
            if number:
                phone['number'] = '+' + number

        # Подготовим операции
        operations_data = self.env.db.select(
            'phone_operations',
            uid=TEST_UID,
            db='passportdbshard1',
        )
        operations = map(dict, operations_data)
        for operation in operations:
            time = operation['password_verified']
            if zero_datetime == time:
                operation['password_verified'] = None

            time = operation['code_confirmed']
            if zero_datetime == time:
                operation['code_confirmed'] = None

        bindings_data = self.env.db.select(
            'phone_bindings',
            uid=TEST_UID,
            db='passportdbshard1',
        )
        bindings = map(dict, bindings_data)
        for binding in bindings:
            if binding['bound'] == zero_datetime:
                binding['type'] = 'unbound'
                binding['bound'] = None
            else:
                raise NotImplementedError()  # pragma: no cover
            binding['number'] = '+%s' % binding['number']

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                phones=phones,
                phone_operations=operations,
                phone_bindings=bindings,
                **bb_kwargs
            ),
        )

    def assert_response_ok(self, rv):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'ok', data)

    def confirm_code(self, operation_id):
        operation = self.get_operation_dict_from_db(operation_id)

        self.set_actual_blackbox_response()
        rv = self.make_request(
            url='/1/bundle/phone/manage/check_code/',
            data={
                'operation_id': operation_id,
                'code': operation['code_value'],
            },
        )
        self.assert_response_ok(rv)

    def check_password(self, operation_id):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
            ),
        )

        self.set_actual_blackbox_response()
        rv = self.make_request(
            url='/1/bundle/phone/manage/check_password/',
            data={'operation_id': operation_id, 'current_password': TEST_PASSWORD},
        )
        self.assert_response_ok(rv)


@with_settings_hosts()
class TestBindPhone(BaseIntegrationalTestCase):
    """
    Привязка обычного телефона к аккаунту.
    """

    def setUp(self):
        super(TestBindPhone, self).setUp()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
            ),
        )

    def test_ok(self):
        rv = self.make_request(
            url='/1/bundle/phone/manage/bind_simple/submit/',
            data={'number': TEST_PHONE_NUMBER.e164, 'display_language': TEST_DISPLAY_LANGUAGE},
        )
        self.assert_response_ok(rv)
        operation_id = json.loads(rv.data)['phone']['operation']['id']

        self.confirm_code(operation_id)

        self.set_actual_blackbox_response()
        rv = self.make_request(
            url='/1/bundle/phone/manage/bind_simple/commit/',
            data={'operation_id': operation_id},
        )
        self.assert_response_ok(rv)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте test изменён номер телефона',
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )


@with_settings_hosts()
class TestBindSecurePhone(BaseIntegrationalTestCase):
    """
    Привязка защищенного телефона к аккаунту.
    """
    def setUp(self):
        super(TestBindSecurePhone, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                crypt_password=TEST_PASSWORD_HASH,
            ),
        )
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def test_ok(self):
        rv = self.make_request(
            url='/1/bundle/phone/manage/bind_secure/submit/',
            data={'number': TEST_PHONE_NUMBER.e164, 'display_language': TEST_DISPLAY_LANGUAGE},
        )
        self.assert_response_ok(rv)
        operation_id = json.loads(rv.data)['phone']['operation']['id']

        self.confirm_code(operation_id)
        self.check_password(operation_id)

        self.set_actual_blackbox_response(crypt_password=TEST_PASSWORD_HASH)
        rv = self.make_request(
            url='/1/bundle/phone/manage/bind_secure/commit/',
            data={'operation_id': operation_id},
        )
        self.assert_response_ok(rv)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='phone_change',
            uid=TEST_UID,
            title='В аккаунте test изменён номер телефона',
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )


@with_settings_hosts()
class TestSecurify(BaseIntegrationalTestCase):
    """
    Делаем обычный телефон защищенным.
    """
    def setUp(self):
        super(TestSecurify, self).setUp()

        bb_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            phones=[
                {'id': TEST_PHONE_ID, 'number': TEST_PHONE_NUMBER.e164, 'bound': TEST_PHONE_BOUND_DT},
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )
        self.env.db.serialize_sessionid(bb_response)
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def test_ok(self):
        rv = self.make_request(
            url='/1/bundle/phone/manage/securify/submit/',
            data={'phone_id': TEST_PHONE_ID, 'display_language': TEST_DISPLAY_LANGUAGE},
        )
        self.assert_response_ok(rv)
        operation_id = json.loads(rv.data)['phone']['operation']['id']

        self.confirm_code(operation_id)
        self.check_password(operation_id)

        self.set_actual_blackbox_response(crypt_password=TEST_PASSWORD_HASH)
        rv = self.make_request(
            url='/1/bundle/phone/manage/securify/commit/',
            data={'operation_id': operation_id},
        )
        self.assert_response_ok(rv)
