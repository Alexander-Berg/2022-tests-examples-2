# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)

from .base import BaseYasmsTestCase


PHONE_NUMBER = u'+79990011222'


class TestCheckPhoneSecureOnly(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        YASMS_PHONE_BINDING_LIMIT=3,
    )

    def test_overview_secure_only_true(self):
        """
        Обзорный тест для случая, когда функция вызывается с secure_only=True.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 24,
                    u'type': u'current',
                    u'uid': 4,
                    u'bound': datetime(2001, 1, 1, 0, 0, 4),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                    attributes={u'phones.secure': 21},
                ),
                dict(
                    uid=4,
                    phones=[{
                        u'id': 24,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 4),
                        u'bound': datetime(2001, 1, 1, 0, 0, 4),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 4),
                    }],
                    attributes={u'phones.secure': 24},
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [
                    {
                        u'uid': 1,
                        u'active': True,
                        u'phoneid': 21,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 1),
                    },
                    {
                        u'uid': 4,
                        u'active': True,
                        u'phoneid': 24,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 4),
                    },
                ],
            },
        )

    def test_use_secure_binding_from_blackbox(self):
        """
        В ответ попадают защищённые связки из ЧЯ.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [
                    {
                        u'uid': 1,
                        u'active': True,
                        u'phoneid': 21,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 1),
                    },
                ],
            },
        )

    def test_no_insecure_binding_from_blackbox(self):
        """
        В ответ не попадают незащищённые привязки из ЧЯ.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                }],
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_number_is_being_bound(self):
        """
        В процессе выполнения подпрограммы телефон удалили и начали
        привязывать заново.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 3),
                    u'bound': None,
                    u'confirmed': None,
                }],
                phone_operations=[{
                    u'phone_id': 21,
                    u'phone_number': PHONE_NUMBER,
                    u'type': u'bind',
                }],
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_removed_user(self):
        """
        В процессе выполнения подпрограммы пользователя удалили.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_removed_phone(self):
        """
        В процессе выполнения подпрограммы телефонный номер удалили.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=1, phones=[]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_admitted_validation_date(self):
        """
        Если есть дата признания, то она использовуется как validation_date.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    u'admitted': datetime(2001, 1, 1, 0, 0, 3),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info[u'items'][0][u'validation_date'],
            datetime(2001, 1, 1, 0, 0, 3),
        )

    def test_confirmed_validation_date(self):
        """
        Если нет даты признания и есть дата подтверждения, то она использовуется
        как validation_date.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(
            phone_info[u'items'][0][u'validation_date'],
            datetime(2001, 1, 1, 0, 0, 2),
        )

    def test_blackbox_requests_when_secure_only_is_true(self):
        """
        У ЧЯ запрашиватся активные привязки и сведения о пользовательских
        телефонах.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(len(self.env.blackbox.requests), 2)

        phone_bindings_requests = self.env.blackbox.get_requests_by_method(u'phone_bindings')
        eq_(len(phone_bindings_requests), 1)
        phone_bindings_requests[0].assert_query_contains({
            u'type': u'current',
            u'numbers': PHONE_NUMBER,
        })

        userinfo_requests = self.env.blackbox.get_requests_by_method(u'userinfo')
        eq_(len(userinfo_requests), 1)
        userinfo_requests[0].assert_post_data_contains({
            u'uid': u'1',
            u'getphones': u'all',
        })

    def test_limit_exceeded(self):
        """
        Если предел связок достигнут, возвращаем такой же результат.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'current',
                    u'uid': 3,
                    u'bound': datetime(2001, 1, 1, 0, 0, 3),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'bound': datetime(2001, 1, 1, 0, 0, 3),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(phone_info[u'binding_limit_exceeded'], True)

    def test_dont_count_bindings_that_should_be_ignored(self):
        """
        Не учитывать связки в ЧЯ, которые нужно игнорировать при подсчёте
        лимитов.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'current',
                    u'uid': 3,
                    u'bound': datetime(2001, 1, 1, 0, 0, 3),
                    u'flags': 1,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                    attributes={u'phones.secure': 21},
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                    attributes={u'phones.secure': 21},
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'bound': datetime(2001, 1, 1, 0, 0, 3),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                    attributes={u'phones.secure': 23},
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=True)

        eq_(phone_info[u'binding_limit_exceeded'], False)


class TestCheckPhoneNotSecureOnly(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        YASMS_PHONE_BINDING_LIMIT=3,
    )

    def test_overview_secure_only_false(self):
        """
        Обзорный тест для случая, когда функция вызывается с secure_only=False.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [
                    {
                        u'uid': 1,
                        u'active': False,
                        u'phoneid': 21,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 1),
                    },
                    {
                        u'uid': 2,
                        u'active': False,
                        u'phoneid': 22,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 2),
                    },
                ],
            },
        )

    def test_secure_bound_unbound_bindings_from_blackbox(self):
        """
        В ответ попадают защищённые связки, обычные связки, отвязанные по лимиту
        учётные записи из ЧЯ.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'unbounud',
                    u'uid': 3,
                    u'bound': None,
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                {
                    u'uid': 1,
                    u'phones': [{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                    u'attributes': {u'phones.secure': 21},
                },
                {
                    u'uid': 2,
                    u'phones': [{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                },
                {
                    u'uid': 3,
                    u'phones': [{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'bound': None,
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                },
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [
                    {
                        u'uid': 1,
                        u'active': True,
                        u'phoneid': 21,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 1),
                    },
                    {
                        u'uid': 2,
                        u'active': False,
                        u'phoneid': 22,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 2),
                    },
                    {
                        u'uid': 3,
                        u'active': False,
                        u'phoneid': 23,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'delivered',
                        u'validation_date': datetime(2001, 1, 1, 0, 0, 3),
                    },
                ],
            },
        )

    def test_removed_user(self):
        """
        В процессе выполнения подпрограммы пользователя удалили.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_number_is_being_bound(self):
        """
        В процессе выполнения подпрограммы телефон удалили и начали
        привязывать заново.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 22,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 3),
                    u'bound': None,
                    u'confirmed': None,
                }],
                phone_operations=[{
                    u'phone_id': 22,
                    u'phone_number': PHONE_NUMBER,
                    u'type': u'bind',
                }],
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_admitted_validation_date(self):
        """
        Если есть дата признания, то она использовуется как validation_date.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    u'admitted': datetime(2001, 1, 1, 0, 0, 3),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info[u'items'][0][u'validation_date'],
            datetime(2001, 1, 1, 0, 0, 3),
        )

    def test_confirmed_validation_date(self):
        """
        Если нет даты признания и есть дата подтверждения, то она использовуется
        как validation_date.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                }],
                attributes={u'phones.secure': 21},
            ),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info[u'items'][0][u'validation_date'],
            datetime(2001, 1, 1, 0, 0, 2),
        )

    def test_removed_phone(self):
        """
        В процессе выполнения подпрограммы телефонный номер удалили.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=1, phones=[]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(
            phone_info,
            {
                u'binding_limit_exceeded': False,
                u'items': [],
            },
        )

    def test_blackbox_requests_when_secure_only_is_false(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=1,
                phones=[{
                    u'id': 21,
                    u'number': PHONE_NUMBER,
                    u'created': datetime(2001, 1, 1, 0, 0, 1),
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                }],
            ),
        )

        self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(len(self.env.blackbox.requests), 2)

        phone_bindings_requests = self.env.blackbox.get_requests_by_method(u'phone_bindings')
        eq_(len(phone_bindings_requests), 1)
        phone_bindings_requests[0].assert_query_contains({
            u'type': u'all',
            u'numbers': PHONE_NUMBER,
        })

        userinfo_requests = self.env.blackbox.get_requests_by_method(u'userinfo')
        eq_(len(userinfo_requests), 1)
        userinfo_requests[0].assert_post_data_contains({
            u'uid': u'1',
            u'getphones': u'all',
        })

    def test_limit_exceeded(self):
        """
        Если ЧЯ сообщает, что предел связок достигнут, возвращаем такой же результат.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'current',
                    u'uid': 3,
                    u'bound': datetime(2001, 1, 1, 0, 0, 3),
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'bound': datetime(2001, 1, 1, 0, 0, 3),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(phone_info[u'binding_limit_exceeded'], True)

    def test_dont_count_bindings_that_should_be_ignored(self):
        """
        Не учитывать связки в ЧЯ, которые нужно игнорировать при подсчёте
        лимитов.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'current',
                    u'uid': 3,
                    u'bound': datetime(2001, 1, 1, 0, 0, 3),
                    u'flags': 1,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'bound': datetime(2001, 1, 1, 0, 0, 3),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(phone_info[u'binding_limit_exceeded'], False)

    def test_dont_count_unbound_bindings(self):
        """
        Не считать отвязки в ЧЯ.
        """
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 21,
                    u'type': u'current',
                    u'uid': 1,
                    u'bound': datetime(2001, 1, 1, 0, 0, 1),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 22,
                    u'type': u'current',
                    u'uid': 2,
                    u'bound': datetime(2001, 1, 1, 0, 0, 2),
                    u'flags': 0,
                },
                {
                    u'number': PHONE_NUMBER,
                    u'phone_id': 23,
                    u'type': u'unbound',
                    u'uid': 3,
                    u'bound': None,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 1),
                        u'bound': datetime(2001, 1, 1, 0, 0, 1),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 1),
                    }],
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 22,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 2),
                        u'bound': datetime(2001, 1, 1, 0, 0, 2),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 2),
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 23,
                        u'number': PHONE_NUMBER,
                        u'created': datetime(2001, 1, 1, 0, 0, 3),
                        u'confirmed': datetime(2001, 1, 1, 0, 0, 3),
                    }],
                ),
            ]),
        )

        phone_info = self._yasms.check_phone(PHONE_NUMBER, secure_only=False)

        eq_(phone_info[u'binding_limit_exceeded'], False)
