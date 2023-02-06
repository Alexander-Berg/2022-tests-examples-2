# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core import Undefined
from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.common.application import (
    Application,
    ApplicationDatabaseReader,
)
from passport.backend.social.common.builders.kolmogor import KolmogorTemporaryError
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_NAME3,
    APPLICATION_SECRET1,
    APPLICATION_SECRET2,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    USER_IP1,
)
from passport.backend.social.common.test.fake_other import FakeBuildApplicationName
from passport.backend.social.common.test.parameterized import (
    param,
    parameterized_expand,
)


AUTHORIZATION_URL1 = 'https://accounts.google.com/o/oauth2/auth?access_type=offline&prompt=consent#footer'
AUTHORIZATION_URL2 = 'https://oauth.vk.com/authorize?v=5.59'

TOKEN_URL1 = 'https://accounts.google.com/o/oauth2/token'
TOKEN_URL2 = 'https://oauth.vk.com/access_token'

REFRESH_TOKEN_URL1 = 'https://accounts.google.com/o/oauth2/refresh_token'

MAX_URL = 'https://www.yandex.ru/' + 'x' * (200 - len('https://www.yandex.ru/'))

MAX_CLIENT_ID_LENGTH = 100
MAX_APPLICATION_DISPLAY_NAME_LENGTH = 100
MAX_SCOPE_LENGTH = 500
MAX_CLIENT_SECRET_LENGTH = 100

VALID_ARGUMENT_VALUES = [
    param('client_id', EXTERNAL_APPLICATION_ID2, model_name='id'),
    param('client_id', '1' * MAX_CLIENT_ID_LENGTH, model_name='id'),
    param('application_display_name', 'Хакеры вывели деньги с карт при помощи Apple Pie', 'display_name'),
    param('application_display_name', '1 «самолёт» — взлёт (скорость 3.5 км), спасибо!', 'display_name'),
    param('application_display_name', 'dom.ru', 'display_name'),
    param('application_display_name', APPLICATION_NAME1, 'display_name'),
    param('application_display_name', '1' * MAX_APPLICATION_DISPLAY_NAME_LENGTH, 'display_name'),
    param('authorization_url', 'https://www.yandex.ru/'),
    param('authorization_url', 'https://www.yandex.ru:443/'),
    param('authorization_url', 'https://www.yandex.ru/?foo=%D0%BF%D1%80'),
    param('authorization_url', MAX_URL),
    param('authorization_url', 'https://яндекс.рф/', model_value='https://xn--d1acpjx3f.xn--p1ai/'),
    param('authorization_url', 'https://xn--d1acpjx3f.xn--p1ai/'),
    param('token_url', 'https://www.yandex.ru/'),
    param('token_url', 'https://www.yandex.ru:443/'),
    param('token_url', 'https://www.yandex.ru/?foo=%D0%BF%D1%80'),
    param('token_url', MAX_URL),
    param('token_url', 'https://яндекс.рф/', model_value='https://xn--d1acpjx3f.xn--p1ai/'),
    param('token_url', 'https://xn--d1acpjx3f.xn--p1ai/'),
    param('refresh_token_url', 'https://www.yandex.ru/'),
    param('refresh_token_url', 'https://www.yandex.ru:443/'),
    param('refresh_token_url', 'https://www.yandex.ru/?foo=%D0%BF%D1%80'),
    param('refresh_token_url', MAX_URL),
    param('refresh_token_url', 'https://яндекс.рф/', model_value='https://xn--d1acpjx3f.xn--p1ai/'),
    param('refresh_token_url', 'https://xn--d1acpjx3f.xn--p1ai/'),
    param('scope', 'foo', model_name='default_scope'),
    param('scope', 'foo bar', model_name='default_scope'),
    param('scope', 'foo,bar', model_name='default_scope'),
    param('scope', '3' * MAX_SCOPE_LENGTH, model_name='default_scope'),
    param('yandex_client_id', EXTERNAL_APPLICATION_ID2, model_name='related_yandex_client_id'),
    param('yandex_client_id', '4' * MAX_CLIENT_ID_LENGTH, model_name='related_yandex_client_id'),
]

MASKABLE_VALID_ARGUMENT_VALUES = [
    param('client_secret', APPLICATION_SECRET2, model_name='secret'),
    param('client_secret', '2' * MAX_CLIENT_SECRET_LENGTH, model_name='secret'),
]

TOO_LONG_URL = 'https://www.yandex.ru/' + 'x' * (201 - len('https://www.yandex.ru/'))

TOO_LONG_VALUES = [
    ('application_display_name', '1' * (MAX_APPLICATION_DISPLAY_NAME_LENGTH + 1)),
    ('client_id', '2' * (MAX_CLIENT_ID_LENGTH + 1)),
    ('client_secret', '3' * (MAX_CLIENT_SECRET_LENGTH + 1)),
    ('authorization_url', TOO_LONG_URL),
    ('token_url', TOO_LONG_URL),
    ('refresh_token_url', TOO_LONG_URL),
    ('scope', '4' * (MAX_SCOPE_LENGTH + 1)),
    ('yandex_client_id', '5' * (MAX_CLIENT_ID_LENGTH + 1)),
]

INVALID_AUTHORIZATION_URLS = [
    ('http://www.yandex.ru/',),
    ('https://credentials@www.yandex.ru/',),
    ('https://login:password@www.yandex.ru/',),
    ('https://:password@www.yandex.ru/',),
    ('https://www.yandex.ru/?foo=привет',),
    ('https://www.yandex.ru/яндекс/',),
]

INVALID_TOKEN_URLS = INVALID_AUTHORIZATION_URLS + [
    ('https://www.yandex.ru/#fragment',),
]

INVALID_CLIENT_IDS = [
    ('привет',),
]

INVALID_APPLICATION_DISPLAY_NAMES = [
    ('Купите наши крутяки (buyshit.ru/)',),
    ('Купите наши <alert>buyshit</alert> крутяки',),
    ('Купите наши <alert href="ололо">buyshit</alert> крутяки',),
    ('Купите наши \n крутяки',),
]


class _BaseStationApplicationTestCase(ApiV3TestCase):
    def build_settings(self):
        settings = super(_BaseStationApplicationTestCase, self).build_settings()
        settings['social_config'].update(
            kolmogor_url='http://kolmogor',
            kolmogor_timeout=1,
            kolmogor_retries=1,
            counter_limit_for_create_application_by_ip=1,
        )
        return settings

    def _build_application_response(self, response=None, exclude=None):
        defaults = {
            'application_name': APPLICATION_NAME1,
            'client_id': EXTERNAL_APPLICATION_ID1,
            'masked_client_secret': '*****',
            'authorization_url': AUTHORIZATION_URL1,
            'token_url': TOKEN_URL1,
        }

        exclude = exclude or list()
        for key in exclude:
            defaults.pop(key, None)

        response = response or dict()
        for key in defaults:
            response.setdefault(key, defaults[key])
        return response

    def _assert_no_application_in_database(self, application_name):
        apps = ApplicationDatabaseReader(self._fake_db.get_engine()).load_by_application_names([application_name])
        self.assertEqual(len(apps), 0)

    def _assert_application_in_database(self, expected_application):
        apps = ApplicationDatabaseReader(self._fake_db.get_engine()).load_by_application_names([expected_application.name])
        self.assertEqual(len(apps), 1)

        app = Application().parse(apps[0])
        self.assertTrue(app.identifier)

        if expected_application.identifier is Undefined:
            expected_application.identifier = app.identifier
        expected_application.parse(dict())
        self.assertEqual(app, expected_application)


class TestCreateStationApplication(_BaseStationApplicationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/api/create_station_application'
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
    }
    REQUEST_DATA = {
        'client_id': EXTERNAL_APPLICATION_ID1,
        'client_secret': APPLICATION_SECRET1,
        'authorization_url': AUTHORIZATION_URL1,
        'token_url': TOKEN_URL1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }

    def setUp(self):
        super(TestCreateStationApplication, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['create-station-application'],
        )
        self._fake_build_application_name = FakeBuildApplicationName().start()

        self._fake_build_application_name.set_retval(APPLICATION_NAME1)
        self._fake_kolmogor.set_response_side_effect('get', ['0'])
        self._fake_kolmogor.set_response_side_effect('inc', ['OK'])

    def tearDown(self):
        self._fake_build_application_name.stop()
        super(TestCreateStationApplication, self).tearDown()

    def _build_application(self):
        return Application(
            name=APPLICATION_NAME1,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            authorization_url=AUTHORIZATION_URL1,
            token_url=TOKEN_URL1,
            domain='social.yandex.net',
            group_id='bass',
            is_third_party=True,
        )

    def _assert_create_station_application_ok_response(self, rv, application_attributes=None,
                                                       exclude_application_attributes=None):
        application_attributes = application_attributes or dict()
        exclude_application_attributes = exclude_application_attributes or list()

        self._assert_ok_response(
            rv,
            response={
                'application': self._build_application_response(
                    application_attributes,
                    exclude_application_attributes,
                ),
            },
        )

    @parameterized_expand(VALID_ARGUMENT_VALUES)
    def test_valid_value(self, form_name, form_value, model_name=None, model_value=None):
        if model_name is None:
            model_name = form_name
        if model_value is None:
            model_value = form_value

        rv = self._make_request(data={form_name: form_value})

        self._assert_create_station_application_ok_response(rv, {form_name: model_value})

        app = self._build_application()
        setattr(app, model_name, model_value)
        self._assert_application_in_database(app)

    @parameterized_expand(MASKABLE_VALID_ARGUMENT_VALUES)
    def test_maskable_valid_value(self, form_name, form_value, model_name=None):
        if model_name is None:
            model_name = form_name

        rv = self._make_request(data={form_name: form_value})

        masked_form_name = 'masked_' + form_name
        self._assert_create_station_application_ok_response(
            rv,
            application_attributes={masked_form_name: '*****'},
            exclude_application_attributes=[form_name],
        )

        app = self._build_application()
        setattr(app, model_name, form_value)
        self._assert_application_in_database(app)

    @parameterized_expand(
        [
            ('client_id',),
            ('client_secret',),
            ('authorization_url',),
            ('token_url',),
        ],
    )
    def test_no_value(self, form_name):
        rv = self._make_request(exclude_data=[form_name])
        self._assert_error_response(rv, ['%s.empty' % form_name])

    @parameterized_expand(
        [
            ('application_display_name'),
            ('client_id',),
            ('client_secret',),
            ('authorization_url',),
            ('token_url',),
            ('refresh_token_url',),
            ('scope',),
            ('yandex_client_id',),
        ],
    )
    def test_empty_value(self, form_name):
        rv = self._make_request(data={form_name: ''})
        self._assert_error_response(rv, ['%s.empty' % form_name])

    @parameterized_expand(TOO_LONG_VALUES)
    def test_too_long_value(self, form_name, value):
        rv = self._make_request(data={form_name: value})
        self._assert_error_response(rv, ['%s.long' % form_name])

    @parameterized_expand(INVALID_APPLICATION_DISPLAY_NAMES)
    def test_invalid_application_display_name(self, value):
        rv = self._make_request(data={'application_display_name': value})
        self._assert_error_response(rv, ['application_display_name.invalid'])

    @parameterized_expand(INVALID_AUTHORIZATION_URLS)
    def test_invalid_authorization_url(self, value):
        rv = self._make_request(data={'authorization_url': value})
        self._assert_error_response(rv, ['authorization_url.invalid'])

    @parameterized_expand(INVALID_TOKEN_URLS)
    def test_invalid_token_url(self, value):
        rv = self._make_request(data={'token_url': value})
        self._assert_error_response(rv, ['token_url.invalid'])

    @parameterized_expand(INVALID_TOKEN_URLS)
    def test_invalid_refresh_token_url(self, value):
        rv = self._make_request(data={'refresh_token_url': value})
        self._assert_error_response(rv, ['refresh_token_url.invalid'])

    @parameterized_expand(INVALID_CLIENT_IDS)
    def test_invalid_yandex_client_id(self, value):
        rv = self._make_request(data={'yandex_client_id': value})
        self._assert_error_response(rv, ['yandex_client_id.invalid'])

    def test_name_not_effect(self):
        rv = self._make_request(data={'application_name': APPLICATION_NAME2})

        self._assert_create_station_application_ok_response(
            rv,
            {'application_name': APPLICATION_NAME1},
        )

        app = self._build_application()
        self.assertNotEqual(app.name, APPLICATION_NAME2)
        self._assert_application_in_database(app)

    def test_generate_name(self):
        self._fake_build_application_name.set_retval(APPLICATION_NAME3)

        rv = self._make_request()

        self._assert_create_station_application_ok_response(
            rv,
            {'application_name': APPLICATION_NAME3},
        )

        app = self._build_application()
        app.name = APPLICATION_NAME3
        self._assert_application_in_database(app)

    def test_rate_limit_exceeded(self):
        self._fake_kolmogor.set_response_side_effect('get', ['1'])
        rv = self._make_request()
        self._assert_error_response(rv, ['rate_limit.exceeded'])

    def test_increase_counter_counter_by_ip(self):
        rv = self._make_request()

        self._assert_create_station_application_ok_response(rv)

        self.assertEqual(len(self._fake_kolmogor.requests), 2)
        self._fake_kolmogor.requests[1].assert_url_starts_with('http://kolmogor/inc')
        self._fake_kolmogor.requests[1].assert_post_data_equals(
            {
                'space': 'socialism',
                'keys': 'create_application_by_ip:' + USER_IP1,
            },
        )

    def test_kolmogor_get_temporary_failed(self):
        self._fake_kolmogor.set_response_side_effect('get', [KolmogorTemporaryError()])
        rv = self._make_request()
        self._assert_error_response(rv, ['internal_error'])

    def test_kolmogor_inc_temporary_failed(self):
        self._fake_kolmogor.set_response_side_effect('inc', [KolmogorTemporaryError()])

        rv = self._make_request()

        self._assert_create_station_application_ok_response(rv)
        self._assert_application_in_database(self._build_application())

    def test_no_user_ip(self):
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])


class TestRemoveStationApplication(_BaseStationApplicationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/api/remove_station_application'
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
    }
    REQUEST_DATA = {
        'application_name': APPLICATION_NAME1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }

    def setUp(self):
        super(TestRemoveStationApplication, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['remove-station-application'],
        )
        app = self._build_application()
        self._session.add(app)
        self._session.commit()

    def _build_application(self):
        return Application(
            identifier=APPLICATION_ID1,
            name=APPLICATION_NAME1,
            id=EXTERNAL_APPLICATION_ID1,
            group_id='bass',
        )

    def test_not_found(self):
        rv = self._make_request(data={'application_name': APPLICATION_NAME2})
        self._assert_ok_response(rv)
        self._assert_application_in_database(self._build_application())

    def test_ok(self):
        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_no_application_in_database(APPLICATION_NAME1)

    def test_other_group_id(self):
        app = self._build_application()
        app.identifier = Undefined
        app.name = APPLICATION_NAME2
        app.id = EXTERNAL_APPLICATION_ID2
        app.group_id = 'passport'
        self._session.add(app)
        self._session.commit()

        rv = self._make_request(data={'application_name': APPLICATION_NAME2})

        self._assert_ok_response(rv)
        self._assert_application_in_database(app)


class TestChangeStationApplication(_BaseStationApplicationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/api/change_station_application'
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
    }
    REQUEST_DATA = {
        'application_name': APPLICATION_NAME1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }

    def setUp(self):
        super(TestChangeStationApplication, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['change-station-application'],
        )

    def _build_application(self):
        return Application(
            identifier=APPLICATION_ID1,
            name=APPLICATION_NAME1,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            authorization_url=AUTHORIZATION_URL1,
            token_url=TOKEN_URL1,
            domain='social.yandex.net',
            group_id='bass',
            is_third_party=True,
        )

    def _assert_change_station_application_ok_response(self, rv, application_attributes=None,
                                                       exclude_application_attributes=None):
        application_attributes = application_attributes or dict()
        exclude_application_attributes = exclude_application_attributes or list()

        self._assert_ok_response(
            rv,
            response={
                'application': self._build_application_response(
                    application_attributes,
                ),
            },
        )

    def test_no_application_name(self):
        rv = self._make_request(exclude_data=['application_name'])
        self._assert_error_response(rv, ['application_name.empty'])

    def test_empty_application_name(self):
        rv = self._make_request(data={'application_name': ''})
        self._assert_error_response(rv, ['application_name.empty'])

    def test_application_not_found(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['application.unknown'])

    def test_application_from_other_group(self):
        app = self._build_application()
        app.group_id = 'passport'
        self._session.add(app)
        self._session.commit()

        rv = self._make_request()

        self._assert_error_response(rv, ['application.unknown'])

    def test_no_changes(self):
        app = self._build_application()
        self._session.add(app)
        self._session.commit()

        rv = self._make_request()

        self._assert_change_station_application_ok_response(rv)
        self._assert_application_in_database(app)

    @parameterized_expand(VALID_ARGUMENT_VALUES)
    def test_valid_value(self, form_name, form_value, model_name=None, model_value=None):
        if model_name is None:
            model_name = form_name
        if model_value is None:
            model_value = form_value

        app = self._build_application()
        self._session.add(app)
        self._session.commit()

        rv = self._make_request(data={form_name: form_value})

        self._assert_change_station_application_ok_response(rv, {form_name: model_value})

        setattr(app, model_name, model_value)
        self._assert_application_in_database(app)

    @parameterized_expand(MASKABLE_VALID_ARGUMENT_VALUES)
    def test_maskable_valid_value(self, form_name, form_value, model_name=None):
        if model_name is None:
            model_name = form_name

        app = self._build_application()
        self._session.add(app)
        self._session.commit()

        rv = self._make_request(data={form_name: form_value})

        masked_form_name = 'masked_' + form_name
        self._assert_change_station_application_ok_response(
            rv,
            application_attributes={masked_form_name: '*****'},
            exclude_application_attributes=[form_name],
        )

        app = self._build_application()
        setattr(app, model_name, form_value)
        self._assert_application_in_database(app)

    @parameterized_expand(
        [
            param('refresh_token_url',),
            param('scope', 'default_scope'),
            param('yandex_client_id', 'related_yandex_client_id'),
        ],
    )
    def test_allowed_empty_value(self, form_name, model_name=None):
        if model_name is None:
            model_name = form_name

        app = self._build_application()
        setattr(app, model_name, 'xxx')
        self._session.add(app)
        self._session.commit()

        rv = self._make_request(data={form_name: ''})

        self._assert_change_station_application_ok_response(rv)

        setattr(app, model_name, Undefined)
        self._assert_application_in_database(app)

    @parameterized_expand(
        [
            ('application_display_name',),
            ('client_id',),
            ('client_secret',),
            ('authorization_url',),
            ('token_url',),
        ],
    )
    def test_not_allowed_empty_value(self, form_name):
        app = self._build_application()
        self._session.add(app)
        self._session.commit()

        rv = self._make_request(data={form_name: ''})

        self._assert_error_response(rv, ['%s.empty' % form_name])

    @parameterized_expand(TOO_LONG_VALUES)
    def test_too_long_value(self, form_name, value):
        rv = self._make_request(data={form_name: value})
        self._assert_error_response(rv, ['%s.long' % form_name])

    @parameterized_expand(INVALID_APPLICATION_DISPLAY_NAMES)
    def test_invalid_application_display_name(self, value):
        rv = self._make_request(data={'application_display_name': value})
        self._assert_error_response(rv, ['application_display_name.invalid'])

    @parameterized_expand(INVALID_AUTHORIZATION_URLS)
    def test_invalid_authorization_url(self, value):
        rv = self._make_request(data={'authorization_url': value})
        self._assert_error_response(rv, ['authorization_url.invalid'])

    @parameterized_expand(INVALID_TOKEN_URLS)
    def test_invalid_token_url(self, value):
        rv = self._make_request(data={'token_url': value})
        self._assert_error_response(rv, ['token_url.invalid'])

    @parameterized_expand(INVALID_TOKEN_URLS)
    def test_invalid_refresh_token_url(self, value):
        rv = self._make_request(data={'refresh_token_url': value})
        self._assert_error_response(rv, ['refresh_token_url.invalid'])

    @parameterized_expand(INVALID_CLIENT_IDS)
    def test_invalid_yandex_client_id(self, value):
        rv = self._make_request(data={'yandex_client_id': value})
        self._assert_error_response(rv, ['yandex_client_id.invalid'])


class TestGetStationApplications(_BaseStationApplicationTestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/api/get_station_applications'
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'application_names': APPLICATION_NAME1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumer-Client-Ip': USER_IP1,
    }

    def setUp(self):
        super(TestGetStationApplications, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['get-station-applications'],
        )

    def _build_application1_response(self, response=None):
        return self._build_application_response(response)

    def _build_application2_response(self, response=None):
        defaults = {
            'application_name': APPLICATION_NAME2,
            'client_id': EXTERNAL_APPLICATION_ID2,
            'masked_client_secret': '*****',
            'authorization_url': AUTHORIZATION_URL2,
            'token_url': TOKEN_URL2,
        }
        response = response or dict()
        for key in defaults:
            response.setdefault(key, defaults[key])
        return response

    def _build_application1(self):
        return Application(
            identifier=APPLICATION_ID1,
            name=APPLICATION_NAME1,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            authorization_url=AUTHORIZATION_URL1,
            token_url=TOKEN_URL1,
            domain='social.yandex.net',
            group_id='bass',
            is_third_party=True,
        )

    def _build_application2(self):
        return Application(
            identifier=APPLICATION_ID2,
            name=APPLICATION_NAME2,
            id=EXTERNAL_APPLICATION_ID2,
            secret=APPLICATION_SECRET2,
            authorization_url=AUTHORIZATION_URL2,
            token_url=TOKEN_URL2,
            domain='social.yandex.net',
            group_id='bass',
            is_third_party=True,
        )

    def test_single(self):
        app = self._build_application1()
        app.refresh_token_url = REFRESH_TOKEN_URL1
        app.default_scope = 'foo bar'
        app.related_yandex_client_id = EXTERNAL_APPLICATION_ID2
        app.display_name = 'hello'
        self._session.add(app)
        self._session.commit()

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response={
                'applications': {
                    APPLICATION_NAME1: self._build_application1_response(
                        {
                            'application_display_name': 'hello',
                            'refresh_token_url': REFRESH_TOKEN_URL1,
                            'scope': 'foo bar',
                            'yandex_client_id': EXTERNAL_APPLICATION_ID2,
                        },
                    ),
                },
            },
        )

    def test_many(self):
        app1 = self._build_application1()
        app2 = self._build_application2()
        self._session.add(app1)
        self._session.add(app2)
        self._session.commit()

        rv = self._make_request(
            query={
                'application_names': APPLICATION_NAME1 + ',' + APPLICATION_NAME2,
            },
        )

        self._assert_ok_response(
            rv,
            response={
                'applications': {
                    APPLICATION_NAME1: self._build_application1_response(),
                    APPLICATION_NAME2: self._build_application2_response(),
                },
            },
        )

    def test_not_found(self):
        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response={
                'applications': {APPLICATION_NAME1: None},
            },
        )

    def test_application_from_other_group(self):
        app = self._build_application1()
        app.group_id = 'passport'
        self._session.add(app)
        self._session.commit()

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response={
                'applications': {APPLICATION_NAME1: None},
            },
        )

    def test_many_applications_from_other_group(self):
        app1 = self._build_application1()
        app1.group_id = 'passport'
        app2 = self._build_application2()
        app2.group_id = 'passport'
        self._session.add(app1)
        self._session.add(app2)
        self._session.commit()

        rv = self._make_request(
            query={
                'application_names': APPLICATION_NAME1 + ',' + APPLICATION_NAME2,
            },
        )

        self._assert_ok_response(
            rv,
            response={
                'applications': {
                    APPLICATION_NAME1: None,
                    APPLICATION_NAME2: None,
                },
            },
        )
