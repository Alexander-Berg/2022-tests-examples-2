# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    nottest,
    ok_,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    BaseBlackboxError,
    Blackbox,
    BlackboxInvalidParamsError,
    BlackboxUnknownError,
)
from passport.backend.core.conf import settings
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.string import smart_bytes


class BaseBlackboxTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager


class BaseBlackboxRequestTestCase(BaseBlackboxTestCase):
    BLACKBOX_RETRIES = 10

    def setUp(self):
        super(BaseBlackboxRequestTestCase, self).setUp()

        self.response = mock.Mock()
        self.blackbox_patch = mock.patch.object(Blackbox, '_request', self.response)
        self.blackbox_patch.start()

        self.blackbox = Blackbox()
        self.blackbox.retries = self.BLACKBOX_RETRIES

    def tearDown(self):
        self.blackbox_patch.stop()
        del self.blackbox_patch
        del self.response
        super(BaseBlackboxRequestTestCase, self).tearDown()

    def set_blackbox_response_value(self, data, status=200):
        # python-requests гарантирует, что content -- это закодированная
        # строка, поэтому, закодируем юникод.
        data = smart_bytes(data)
        self.response.return_value = mock.Mock(
            content=data,
            status_code=status,
            encoding=u'utf-8',
        )

    def set_blackbox_response_error(self, error_code, error_message=b''):
        self.set_blackbox_response_value(
            b'{"exception": {"value": "%s"}, "error":"%s"}' % (error_code, error_message),
        )

    def set_blackbox_side_effect(self, se):
        self.response.side_effect = se

    def get_methods_and_args(self):
        """Возвращает набор из всех методов ЧЯ и параметров для их вызова"""
        return [
            (self.blackbox.userinfo, (0,)),
            (self.blackbox.pwdhistory, (0, '', 5)),
            (self.blackbox.test_pwd_hashes, ('password', ['hash1', 'hash2'], 123)),
            (self.blackbox.create_pwd_hash, ('1', 12345, 'password')),
            (self.blackbox.hosted_domains, (0,)),
            (self.blackbox.loginoccupation, ([''],)),
            (self.blackbox.createsession, (1, '127.0.0.1', 'yandex.ru', 5)),
            (self.blackbox.editsession, ('select', 'sessionid', 1, '127.0.0.1', 'yandex.ru')),
            (self.blackbox.oauth, ('123', '127.0.0.1')),
            (self.blackbox.sessionid, ('123', '127.0.0.1', '.yandex.ru')),
            (self.blackbox.login, ('testlogin', 'testpassword', '127.0.0.1')),
            (self.blackbox.find_pdd_accounts, (None, 'okna.ru', '*')),
            (self.blackbox.check_device_signature, ('nonce', 'sign_space', 'device_id', 'signature')),
        ]

    def base_params(self, base_params, exclude=None, **kwargs):
        params = merge_dicts(base_params, kwargs)
        if exclude is not None:
            for key in exclude:
                del params[key]
        return params


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class TestBlackboxRequest(BaseBlackboxRequestTestCase):

    def test_blackbox_retries_error(self):
        self.set_blackbox_response_error(b'DB_FETCHFAILED')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(BaseBlackboxError):
                method(*args)
        eq_(self.blackbox._request.call_count, 10 * (i + 1))

    def test_blackbox_access_denied_error(self):
        self.set_blackbox_response_error(b'ACCESS_DENIED')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(AccessDenied):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_blackbox_invalid_params_error(self):
        self.set_blackbox_response_error(b'INVALID_PARAMS')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(BlackboxInvalidParamsError):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_blackbox_user_error(self):
        self.set_blackbox_response_value(b'{"users": [{"exception": {"value": "ACCESS_DENIED"}, "error":""}]}')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(AccessDenied):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_blackbox_second_user_error(self):
        self.set_blackbox_response_value(b'{"users": [{"uid": {}}, {"exception": '
                                         b'{"value": "ACCESS_DENIED"}, "error":""}]}')

        for i, (method, args) in enumerate([(self.blackbox.userinfo, (0,)),
                                            (self.blackbox.pwdhistory, (0, '', 5)),
                                            (self.blackbox.loginoccupation, ([''],))]):
            with assert_raises(AccessDenied):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_invalid_json(self):
        self.set_blackbox_response_value('{')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(BaseBlackboxError):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_unknown_blackbox_error(self):
        self.set_blackbox_response_value(b'{"users": [{"uid": {}}, {"exception": {"value": "UNKNOWN"}, "error":""}]}')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(BlackboxUnknownError):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_unexpected_blackbox_error(self):
        self.set_blackbox_response_error(b'YET-ANOTHER-ERROR')

        for i, (method, args) in enumerate(self.get_methods_and_args()):
            with assert_raises(BaseBlackboxError):
                method(*args)
        eq_(self.blackbox._request.call_count, i + 1)

    def test_blackbox_encoded_error__ok(self):
        """Сообщения об ошибках декодируются из utf-8"""

        error__expected_message = [
            (b'\xd1\x83andex', u'\u0443andex'),  # строчка в utf
            (b'.\xd1\x80\xd1\x83', u'.\u0440\u0443'),  # не прошла кодировка в idna
            (
                u'\u044f\u043d\u0434\u0435\u043a\u0441'.encode('utf-8'),  # unicode OK
                u'\u044f\u043d\u0434\u0435\u043a\u0441',
            ),
        ]

        for error, expected_message in error__expected_message:
            self.set_blackbox_response_value(
                b'{"users": [{"uid": {}}, {"exception": {"value": "UNKNOWN"}, "error":"%s"}]}' % error,
            )
            try:
                self.blackbox.userinfo(0)
            except BaseBlackboxError as ex:
                eq_(ex.args[0], expected_message)


@nottest
class TestPhoneArguments(object):
    def __init__(self, build_request_info):
        self._build_request_info = build_request_info

    def assert_request_phones_is_all_when_phones_arg_value_is_all(self):
        request_info = self._build_request_info(phones=u'all', phone_attributes=[])

        self._request_contains_args(request_info, {u'getphones': u'all'})

    def assert_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty(self):
        request_info = self._build_request_info(
            phones=u'all',
            phone_attributes=[u'created', u'bound'],
        )

        self._request_contains_args(
            request_info,
            {u'phone_attributes': u'%d,%d' % (
                EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[u'created'],
                EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[u'bound'],
            )},
        )

    def assert_request_has_no_phone_attributes_when_phone_attributes_is_empty(self):
        request_info = self._build_request_info(
            phones=u'all',
            phone_attributes=[],
        )

        self._request_does_not_contain_args(request_info, [u'phone_attributes'])

    def assert_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty(self):
        request_info = self._build_request_info(
            phones=None,
            phone_attributes=[u'created', u'bound'],
        )

        self._request_does_not_contain_args(request_info, [u'phone_attributes'])

    def assert_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none(self):
        request_info = self._build_request_info(
            phones=u'all',
            phone_attributes=None,
        )

        default_attr_types = [
            EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[attr_name]
            for attr_name in settings.BLACKBOX_PHONE_EXTENDED_ATTRIBUTES
        ]

        self._request_contains_args(
            request_info,
            {u'phone_attributes': u','.join(map(str, default_attr_types))},
        )

    def assert_request_get_phone_operations_is_one_when_need_phone_operations_is_true(self):
        request_info = self._build_request_info(
            need_phone_operations=True,
        )

        self._request_contains_args(request_info, {u'getphoneoperations': u'1'})

    def assert_request_has_no_phone_operations_when_need_phone_operations_is_false(self):
        request_info = self._build_request_info(
            need_phone_operations=False,
        )

        self._request_does_not_contain_args(request_info, u'getphoneoperations')

    def test_phone_bindings(self):
        self._request_does_not_contain_args(
            self._build_request_info(),
            u'getphonebindings',
        )
        self._request_contains_args(
            self._build_request_info(need_current_phone_bindings=True),
            {u'getphonebindings': 'current'},
        )
        self._request_contains_args(
            self._build_request_info(need_unbound_phone_bindings=True),
            {u'getphonebindings': 'unbound'},
        )
        self._request_contains_args(
            self._build_request_info(
                need_current_phone_bindings=True,
                need_unbound_phone_bindings=True,
            ),
            {u'getphonebindings': 'all'},
        )

    def _request_contains_args(self, r, args):
        get_args = r.get_args or {}
        post_args = r.post_args or {}
        for arg_name in args:
            ok_(
                not (arg_name in get_args and arg_name in post_args),
                u'"%s" in both query arguments and post arguments' % arg_name,
            )
            ok_(
                arg_name in get_args or arg_name in post_args,
                u'Request does not contain "%s" arg' % arg_name,
            )

    def _request_does_not_contain_args(self, r, args):
        get_args = r.get_args or {}
        post_args = r.post_args or {}
        for arg_name in args:
            ok_(
                arg_name not in get_args and arg_name not in post_args,
                u'"%s" in query arguments' % arg_name,
            )
