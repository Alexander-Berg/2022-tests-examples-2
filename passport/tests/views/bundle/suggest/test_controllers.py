# -*- coding: utf-8 -*-
from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.common.processes import (
    ALL_PROCESSES,
    PROCESS_WEB_REGISTRATION,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER,
    TEST_FIRSTNAME,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


TEST_LONG_LOGIN = 'long-login'


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES={'all': ['en', 'ru'], 'default': 'en'},
    MOBILE_FALLBACKS={'kk': 'kk', 'ky': 'ru', 'ru': 'ru'},
)
class SuggestMobileLanguageTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/suggest/mobile_language/'

    http_method = 'get'

    http_query_args = dict(
        consumer=TEST_CONSUMER,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'language': ['suggest'],
                },
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.http_query_args.update(track_id=self.track_id)

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def test_without_ip(self):
        self.assert_ok_response(self.make_request(headers={'accept_language': 'ru'}), **{'language': 'ru'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'kk'}), **{'language': 'kk'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'ky'}), **{'language': 'ru'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'en'}), **{'language': 'en'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'thl'}), **{'language': 'en'})

    def test_ip(self):
        self.assert_ok_response(self.make_request(headers={'user_ip': '8.8.8.8'}), **{'language': 'en'})
        self.assert_ok_response(self.make_request(headers={'user_ip': '213.180.195.32'}), **{'language': 'ru'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'en', 'user_ip': '213.180.195.32'}), **{'language': 'en'})
        self.assert_ok_response(self.make_request(headers={'accept_language': 'thl', 'user_ip': '213.180.195.32'}), **{'language': 'en'})


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    LOGIN_SUGGESTIONS_LIMIT=3,
    LOGIN_SUGGEST_MAX_ITERATIONS=10,
    LANG_TO_MIXES={'ru': []},
)
class SuggestLoginTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/suggest/login/'

    http_method = 'get'
    http_query_args = dict(
        first_name=TEST_FIRSTNAME,
        last_name=TEST_LASTNAME,
        login=TEST_LOGIN,
        language=TEST_LANGUAGE,
        consumer=TEST_CONSUMER,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'login': ['suggest'],
                },
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(
            process_name=PROCESS_WEB_REGISTRATION,
        )
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.http_query_args.update(track_id=self.track_id)

        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_USER_IP,
            consumer=TEST_CONSUMER,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'suggest_error',
            action='suggest_login_error',
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            login=TEST_LONG_LOGIN,
            track_id=self.track_id,
        )

    @property
    def expected_response(self):
        return {
            'suggested_logins': [TEST_LOGIN],
        }

    def setup_bb_response(self, logins):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(logins),
        )

    def setup_bb_side_effect(self, logins_packs):
        self.env.blackbox.set_response_side_effect(
            'loginoccupation',
            [blackbox_loginoccupation_response(logins) for logins in logins_packs],
        )

    def assert_track_ok(self, suggested_logins=None, first_call=None, counter=1):
        track = self.track_manager.read(self.track_id)
        suggested_logins = suggested_logins or []
        if suggested_logins:
            eq_(list(track.suggested_logins.get()), suggested_logins)
        eq_(track.suggest_login_count.get(), counter)
        eq_(track.suggest_login_first_call, first_call or TimeNow())
        eq_(track.suggest_login_last_call, TimeNow())

    @parameterized.expand([process for process in ALL_PROCESSES if process != PROCESS_WEB_REGISTRATION])
    def test_invalid_track_process(self, process):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(
            process_name=process,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_form_invalid__error(self):
        resp = self.make_request(exclude_args=['first_name', 'last_name', 'login'])
        self.assert_error_response(resp, ['form.invalid'])

    def test_login_free__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[TEST_LOGIN], []])
        self.setup_bb_response({TEST_LOGIN: 'free'})
        resp = self.make_request()
        self.assert_ok_response(resp, suggested_logins=[])
        self.env.statbox.assert_has_written([])
        self.assert_track_ok()

    def test_login_lowercase_free__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[TEST_LOGIN], []])
        self.setup_bb_response({TEST_LOGIN: 'free'})
        resp = self.make_request(query_args={'login': 'LOgin'})
        self.assert_ok_response(resp, suggested_logins=[])
        self.env.statbox.assert_has_written([])
        self.assert_track_ok()

    def test_email_in_login_occupied__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[TEST_LOGIN], []])
        self.setup_bb_response({TEST_LOGIN: 'occupied'})
        resp = self.make_request(query_args={'login': 'login@ya.ru'})
        self.assert_ok_response(resp, suggested_logins=[])
        self.env.statbox.assert_has_written([])

    def test_email_in_login_invalid__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[TEST_LOGIN], []])
        self.setup_bb_response({TEST_LOGIN: 'free'})
        resp = self.make_request(query_args={'login': 'login--@ya.ru'})
        self.assert_ok_response(resp, **self.expected_response)
        self.env.statbox.assert_has_written([])

    def test_no_suggested_logins__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        resp = self.make_request()
        self.assert_ok_response(resp, suggested_logins=[])
        self.assert_track_ok()

    def test_no_suggestions_and_long_login__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        resp = self.make_request(query_args={'login': TEST_LONG_LOGIN})
        self.assert_ok_response(resp, suggested_logins=[])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('suggest_error'),
        ])

    def test_suggested_logins__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['galen.erso', 'k2.so'],
            ['cassian'],
            [],
        ])
        self.setup_bb_side_effect(
            logins_packs=[
                {'galen.erso': 'free', 'k2.so': 'free'},
                {'cassian': 'occupied'},
            ],
        )
        resp = self.make_request()
        expected_response = [
            'galen.erso',
            'k2.so',
        ]
        self.assert_ok_response(resp, suggested_logins=expected_response)
        self.env.statbox.assert_has_written([])
        self.assert_track_ok(suggested_logins=['galen.erso', 'k2.so'])

    def test_suggested_logins_and_entered_free__ok(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            [TEST_LOGIN, 'galen.erso'],
            [],
        ])
        self.setup_bb_response({'galen.erso': 'free'})
        resp = self.make_request()
        self.assert_ok_response(resp, suggested_logins=['galen.erso'])
        self.env.statbox.assert_has_written([])
        self.assert_track_ok(suggested_logins=['galen.erso'])
        self.env.blackbox.requests[0].assert_query_contains({
            'logins': ['galen.erso'],
            'method': 'loginoccupation',
            'format': 'json',
        })

    def test_with_existing_track(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['galen.erso'],
            ['k2.so'],
            ['cassian'],
            [],
        ])
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.suggested_logins.append(TEST_LOGIN)
            track.suggest_login_first_call = 123
            track.suggest_login_last_call = 123
            track.suggest_login_count.incr()

        self.setup_bb_side_effect(
            logins_packs=[
                {'galen.erso': 'free'},
                {'k2.so': 'free'},
                {'cassian': 'malformed'},
            ],
        )
        resp = self.make_request()
        expected_response = [
            'galen.erso',
            'k2.so',
        ]
        self.assert_ok_response(resp, suggested_logins=expected_response)
        self.env.statbox.assert_has_written([])
        self.assert_track_ok(
            suggested_logins=[TEST_LOGIN, 'galen.erso', 'k2.so'],
            first_call='123',
            counter=2,
        )

    def test_available_logins_only__not_yandex_ip(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['phne-free'],
            ['uid-free'],
            ['yandex-team-free'],
            ['yndx-free'],
            ['cassian'],
            [],
        ])

        self.setup_bb_side_effect(
            logins_packs=[
                {'cassian': 'free'},
            ],
        )
        resp = self.make_request(query_args={'login': 'yndx-free'}, headers={'user_ip': '8.8.8.8'})
        expected_response = ['cassian']
        self.assert_ok_response(resp, suggested_logins=expected_response)
        self.env.statbox.assert_has_written([])
        self.assert_track_ok(suggested_logins=['cassian'])
        self.env.blackbox.requests[-1].assert_query_contains({
            'logins': ['cassian'],
            'method': 'loginoccupation',
            'format': 'json',
        })

    def test_available_logins_only__yandex_ip(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['phne-free', 'uid-free', TEST_LOGIN, 'yandex-team-free'],
            ['yndx-free', 'yndx-occupied'],
            [],
        ])

        self.setup_bb_side_effect(
            logins_packs=[
                {
                    TEST_LOGIN: 'occupied',
                    'yandex-team-free': 'free',
                },
                {
                    'yndx-free': 'free',
                    'yndx-occupied': 'occupied',
                },
            ],
        )
        resp = self.make_request(headers={'user_ip': '37.9.101.188'})
        expected_response = [
            'yandex-team-free',
            'yndx-free',
        ]
        self.assert_ok_response(resp, suggested_logins=expected_response)
        self.env.statbox.assert_has_written([])
        self.assert_track_ok(suggested_logins=expected_response)
        self.env.blackbox.requests[-1].assert_query_contains({
            'method': 'loginoccupation',
            'format': 'json',
        })
