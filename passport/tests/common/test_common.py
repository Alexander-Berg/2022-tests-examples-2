# -*- coding: utf-8 -*-

from unittest import TestCase

from formencode.validators import Invalid
import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.common import (
    check_spammer,
    CleanWebChecker,
    escape_query_characters_middleware,
    get_email_domain,
    parse_args_for_track,
)
from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.core.builders.blackbox.exceptions import BaseBlackboxError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_phone_bindings_response
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_simple_response_user_data,
)
from passport.backend.core.builders.frodo.faker import frodo_check_response
from passport.backend.core.env import Environment
from passport.backend.core.models.account import Account
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_PHONE_NUMBER1,
    TEST_TRACK_ID1,
)
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.tracks.model import AuthTrack
from passport.backend.core.types.display_name import DisplayName


def test_parse_args_for_track():
    """
    Вспомогательная функция не теряет параметры в зависимости от их значений.
    Должна выбрасывать те что указаны явно как `exclude` и те что равны `None`
    """
    valid_args = {
        'key1': 'qwerty',
        'key2': '0',
        'key3': 'false',
        'key4': 'true',
        'key5': '',
        'key6': False,
        'key7': True,
    }
    incoming_args = dict(valid_args,
                         consumer='dev',
                         id='123',
                         invalid_key=None)
    track_args = parse_args_for_track(incoming_args, exclude=['id'])
    eq_(track_args, valid_args)


@with_settings
def test_get_email_domain():
    zones = {'ru': 'ru', 'com': 'com', 'com.tr': 'com', 'ua': 'ua',
             'by': 'by', 'kz': 'kz'}
    domains = ('yandex.',)
    valid_hosts = ((d + z, d + zz) for d in domains for z, zz in zones.items())
    invalid_hosts = (
        u'somesite.com',
        u'blogs.yandex.ru/derpina/?blobpost=duckface3',
        u'b91647b&^(B$B%7',
        u'.ru',
        u'com.tr',
        u'yandex.ru.zloyvasya.ru',
        u'nyandex.ru',
        u'уаndex.ru',  # cyrillic 'у, a, е'
        u'yandex.kewlhaxxor.ru',
        u'yandex.ru.ru',
        u'yandex.ru//dobryvasya.com',
    )

    for host, email_domain in valid_hosts:
        eq_(get_email_domain(host), email_domain)

    for host in invalid_hosts:
        eq_(get_email_domain(host), 'yandex.com')


def test_escape_query_characters_middleware():
    wsgi_app = mock.Mock(name=u'wsgi_app', __name__='wsgi_app')
    middleware = escape_query_characters_middleware(wsgi_app)

    environ = {
        'QUERY_STRING': 'a\n\r= 1\n',
        'OTHER_VAR': 'OTHER_VAR\nVALUE',
    }
    start_response = mock.Mock(name=u'start_response')
    retval = middleware(environ, start_response)

    wsgi_app.assert_called_once_with(environ, start_response)
    eq_(retval, wsgi_app.return_value)
    eq_(environ['QUERY_STRING'], 'a%0A%0D=%201%0A')
    eq_(environ['OTHER_VAR'], 'OTHER_VAR\nVALUE')


@with_settings()
class TestCheckSpammer(TestCase):
    def setUp(self):
        super(TestCheckSpammer, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_frodo()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestCheckSpammer, self).tearDown()

    def setup_frodo(self):
        self.env.frodo.set_response_value('check', frodo_check_response())

    def build_args(self, confirmed_phone=None):
        account = Account().parse({})
        env = Environment()
        frodo_args = dict()
        track = AuthTrack(track_id=TEST_TRACK_ID1)
        consumer = TEST_CONSUMER1

        if confirmed_phone is not None:
            track.phone_confirmation_phone_number = confirmed_phone.e164
            track.phone_confirmation_is_confirmed = True

        return account, env, frodo_args, track, consumer

    def test_no_phone_bindings(self):
        self.env.blackbox.set_response_value('phone_bindings', blackbox_phone_bindings_response([]))

        check_spammer(*self.build_args(confirmed_phone=TEST_PHONE_NUMBER1))

        self.env.frodo.requests[0].assert_query_contains({
            'phonenumber': TEST_PHONE_NUMBER1.masked_format_for_frodo,
            'v2_phone_bindings_count': '0',
        })

    def test_has_phone_bindings(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([
                dict(
                    number=TEST_PHONE_NUMBER1.e164,
                    type='current',
                ),
            ]),
        )

        check_spammer(*self.build_args(confirmed_phone=TEST_PHONE_NUMBER1))

        self.env.frodo.requests[0].assert_query_contains({
            'phonenumber': TEST_PHONE_NUMBER1.masked_format_for_frodo,
            'v2_phone_bindings_count': '1',
        })

    def test_getting_phone_bindings_failed(self):
        self.env.blackbox.set_response_side_effect('phone_bindings', BaseBlackboxError())

        check_spammer(*self.build_args(confirmed_phone=TEST_PHONE_NUMBER1))

        self.env.frodo.requests[0].assert_query_contains({
            'phonenumber': TEST_PHONE_NUMBER1.masked_format_for_frodo,
            'v2_phone_bindings_count': '0',
        })


@with_settings(
    CLEAN_WEB_API_ENABLED=True,
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=2,
)
class TestCleanWebChecker(TestCase):
    def setUp(self):
        super(TestCleanWebChecker, self).setUp()
        self.env = ViewsTestEnvironment()
        request_mock = mock.Mock()
        request_mock.env.request_id = 'request_id'
        self._request_patch = mock.patch('passport.backend.api.common.common.request', request_mock)
        self._request_patch.start()
        self.env.start()
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data(True))

    def tearDown(self):
        self.env.stop()
        self._request_patch.stop()
        del self.env
        del self._request_patch
        super(TestCleanWebChecker, self).tearDown()

    def check_request(self, first_name=None, last_name=None, full_name=None, display_name=None):
        eq_(len(self.env.clean_web_api.requests), 1)
        data = {
            k: v for
            k, v in dict(
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                display_name=display_name,
            ).items()
            if v is not None
        }
        self.env.clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=(
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'user_data',
                        'service': 'passport',
                        'body': dict(
                            data,
                            auto_only=True,
                        ),
                        'key': 'FAKE_KEY-request_id',
                    },
                )
            )
        )

    @parameterized.expand([
        (dict(firstname='Elon'), dict(first_name='Elon')),
        (dict(firstname=u'Илон'), dict(first_name=u'Илон')),
        (dict(display_name=DisplayName('Elon')), dict(display_name='Elon')),
        (dict(display_name=DisplayName(u'Илон')), dict(display_name=u'Илон')),
        (dict(firstname='Elon', lastname='Musk'), dict(first_name='Elon', last_name='Musk', full_name='Elon Musk')),
        (dict(firstname=u'Илон', lastname='Musk'), dict(first_name=u'Илон', last_name='Musk', full_name=u'Илон Musk')),
        (dict(firstname=u'Илон', lastname=u'Маск'), dict(first_name=u'Илон', last_name=u'Маск', full_name=u'Илон Маск')),
        (dict(firstname='Elon', lastname='Musk', display_name=DisplayName('Test')), dict(first_name='Elon', last_name='Musk', full_name='Elon Musk', display_name='Test')),
    ])
    def test_ok(self, form, request_data):
        CleanWebChecker().check_form_values(form)
        self.check_request(**request_data)

    @parameterized.expand([
        (dict(firstname='Elon'), dict(first_name='Elon')),
        (dict(firstname=u'Илон'), dict(first_name=u'Илон')),
        (dict(firstname='Elon', display_name=DisplayName('Elon')), dict(first_name='Elon', display_name='Elon')),
        (dict(firstname='Elon', display_name=DisplayName(u'Илон')), dict(first_name='Elon', display_name=u'Илон')),
    ])
    def test_bad_first_name(self, form, request_data):
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data(['first_name']))

        class TestException(Exception):
            pass

        with assert_raises(TestException):
            CleanWebChecker().check_form_values(form, error_class=TestException)
        self.check_request(**request_data)

    @parameterized.expand([
        (dict(firstname='Elon'), dict(first_name='Elon')),
        (dict(firstname=u'Илон'), dict(first_name=u'Илон')),
        (dict(display_name=DisplayName('Elon')), dict(display_name='Elon')),
        (dict(display_name=DisplayName(u'Илон')), dict(display_name=u'Илон')),
        (dict(firstname='Elon', lastname='Musk'), dict(first_name='Elon', last_name='Musk', full_name='Elon Musk')),
        (dict(firstname=u'Илон', lastname='Musk'), dict(first_name=u'Илон', last_name='Musk', full_name=u'Илон Musk')),
        (dict(firstname=u'Илон', lastname=u'Маск'), dict(first_name=u'Илон', last_name=u'Маск', full_name=u'Илон Маск')),
        (dict(firstname='Elon', lastname='Musk', display_name=DisplayName('Test')), dict(first_name='Elon', last_name='Musk', full_name='Elon Musk', display_name='Test')),
    ])
    def test_bad_everything(self, form, request_data):
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data([k for k in request_data]))

        class TestException(Exception):
            pass

        with assert_raises(TestException):
            CleanWebChecker().check_form_values(form, error_class=TestException)
        self.check_request(**request_data)

    @parameterized.expand([
        # Формат кортежа: параметры для формы, ответ ЧВ, ожидаемые ошибки формы
        (dict(firstname=u'ok', lastname=u'ok'), [], set()),
        (dict(firstname=u'плохо', lastname=u'ok'), ['first_name', 'full_name'], {'firstname'}),
        (dict(firstname=u'ok', lastname=u'плохо'), ['last_name', 'full_name'], {'lastname'}),
        (dict(firstname=u'плохо', lastname=u'плохо'), ['first_name', 'last_name', 'full_name'],
         {'firstname', 'lastname'}),
        (dict(firstname=u'пло', lastname=u'хо'), ['full_name'], {'firstname', 'lastname'}),
        (dict(firstname=u'плохое китайское фио', lastname=u'на русском языке', display_name=DisplayName('display name')),
         ['first_name', 'last_name', 'display_name'],
         {'display_name'}),
        (dict(firstname=u'плохое китайское фио', lastname=u'на русском языке'), ['first_name', 'last_name'], set()),
    ])
    def test_full_name(self, form, request_data, form_errors):
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data(request_data))

        try:
            CleanWebChecker().check_form_values(form)
        except Invalid as e:
            if not form_errors:
                assert False, "Unexpected form error {}".format(repr(e))
            assert set(e.error_dict) == form_errors
        else:
            assert not form_errors
