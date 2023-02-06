# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.conf import settings
from passport.backend.core.test.cookiemy_for_language import cookiemy_for_language
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(
    FIO_SUGGEST_API_URL='http://localhost',
)
class TestSuggest(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                networks=[
                    '127.0.0.1',
                    '144.122.145.170',
                    '213.180.195.32',
                    '8.8.8.8',
                ],
            ),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.env.fio_suggest.set_response_value('get', '{}')
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'suggest_login_error',
            action='suggest_login_error',
        )

    def check_suggest(self, url, data, response, **kwargs):
        response.update({'status': 'ok'})
        rv = self.env.client.post('/1/suggest/%s/?consumer=dev' % url, data=data, **kwargs)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(json.loads(rv.data), response)

    def test_suggest_name(self):
        self.check_suggest('name', {'name': 'Adam Smith'}, {'firstname': 'Adam', 'lastname': 'Smith'})

    def test_suggest_name_max_length(self):
        self.check_suggest('name', {'name': 'A' * 100}, {'firstname': '', 'lastname': 'A' * 50})
        self.check_suggest('name', {'name': '%s %s' % ('A' * 60, 'B' * 60)},
                           {'firstname': 'B' * 50, 'lastname': 'A' * 50})

    def test_suggest_ru_name(self):
        self.check_suggest('name', {'name': u'Роман Иванов'}, {'firstname': u'Роман', 'lastname': u'Иванов'})

    def test_suggest_name_track_counter(self):
        self.check_suggest(
            'name',
            {'name': 'Adam Smith', 'track_id': self.track_id},
            {'firstname': 'Adam', 'lastname': 'Smith'},
        )
        self.check_suggest(
            'name',
            {'name': 'Adam Smith', 'track_id': self.track_id},
            {'firstname': 'Adam', 'lastname': 'Smith'},
        )
        eq_(self.track_manager.read(self.track_id).suggest_name_count.get(), 2)

    def test_suggest_login_like_email(self):
        test_map = [
            ({'login': 'foo+bar@xxx.yyy'}, {'logins': ['foo', 'bar']}),
            ({'login': '---foo---@xxx.yyy'}, {'logins': ['foo', 'bar']}),
        ]
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'foo': 'free', 'bar': 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([['foo', 'bar'], []] * len(test_map))
        for i, (actual, expected) in enumerate(test_map):
            actual.update({'track_id': self.track_id})
            self.check_suggest('login', actual, expected)
            eq_(self.track_manager.read(self.track_id).suggest_login_count.get(), i + 1)
            self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_like_entered_skipped(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'bar': 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([['bar', 'foo'], []])
        self.check_suggest('login', {'login': 'foo'}, {'logins': ['bar']})
        eq_(self.env.blackbox.request.call_count, 1)
        self.env.blackbox.requests[0].assert_query_contains(
            {
                'method': 'loginoccupation',
                'logins': ['bar'],
                'format': 'json',
            },
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_like_email_occupied(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'foo': 'occupied', 'bar': 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([['bar', 'foo'], []])
        self.check_suggest(
            'login',
            {'login': 'foo@bar.zar'},
            {'logins': ['bar']},
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_empty_suggest_like_email_login_too_long(self):
        long_login = 'tooooooooooooloooooooonggggggloginnnnnnnnnnnnnnnn'
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({long_login: 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        self.check_suggest(
            'login',
            {'login': long_login + '@bar.zar'},
            {'logins': []},
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('suggest_login_error', login=long_login),
        ])

    def test_suggest_login_bad_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'bar': 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([['bar'], []])
        self.check_suggest(
            'login',
            {'login': '1bar--2..+'},
            {'logins': ['bar']},
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test1': 'free', 'test2': 'free'}),
        )
        expected = ['test1', 'test2']
        self.env.login_suggester.setup_next_pack_side_effect([expected, []] * 3)
        self.check_suggest(
            'login',
            {'firstname': 'al', 'lastname': 'bl', 'language': 'ru', 'login': 'aaa'},
            {'logins': expected},
        )
        self.check_suggest(
            'login',
            {'login': 'aaa', 'language': 'ru', 'track_id': self.track_id},
            {'logins': expected},
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            eq_(set(track.suggested_logins.get()), set(expected))
            eq_(track.suggest_login_first_call, TimeNow())
            eq_(track.suggest_login_last_call, TimeNow())
            track.suggest_login_first_call = 123
        # Проверяем, что suggest_login_first_call записывается только один раз
        self.check_suggest(
            'login',
            {'login': 'aaa', 'language': 'ru', 'track_id': self.track_id},
            {'logins': expected},
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.suggest_login_first_call, '123')
        eq_(track.suggest_login_last_call, TimeNow())
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_with_phone_number(self):
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        self.check_suggest(
            'login',
            {'login': 'aaa', 'phone_number': '+79261234567'},
            {'logins': []},
        )
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_empty_suggest_short_login(self):
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        self.check_suggest(
            'login',
            {'login': 'aaa', 'track_id': self.track_id},
            {'logins': []},
        )
        eq_(self.track_manager.read(self.track_id).suggested_logins.get(), [])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_cyrillic(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'foo': 'free', 'bar': 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([['foo', 'bar'], []])
        self.check_suggest(
            'login',
            {'firstname': u'Вася', 'lastname': u'Иванов', 'language': 'ru'},
            {'logins': ['foo', 'bar']},
        )
        eq_(self.env.login_suggester._mock.call_count, 2)
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_track_counter(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'loginoccupation',
            [
                blackbox_loginoccupation_response({'bl.al': 'free', 'al.bl': 'free'}),
                blackbox_loginoccupation_response({'bl.al1': 'free', 'al.bl2': 'free'}),
            ],
        )
        self.env.login_suggester.setup_next_pack_side_effect([['bl.al', 'al.bl'], [], ['bl.al1', 'al.bl2'], []])
        self.check_suggest(
            'login',
            {'track_id': self.track_id, 'firstname': 'al', 'lastname': 'bl', 'language': 'ru', 'login': 'a'},
            {'logins': ['bl.al', 'al.bl']},
        )
        self.check_suggest(
            'login',
            {'track_id': self.track_id, 'firstname': 'al1', 'lastname': 'bl2', 'language': 'ru', 'login': 'a'},
            {'logins': ['bl.al1', 'al.bl2']},
        )

        eq_(self.track_manager.read(self.track_id).suggest_login_count.get(), 2)
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_suggest_login_statbox_logs(self):
        login = 'testlogin'
        firstname = 'firstname'
        lastname = 'lastname'
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({login: 'free'}),
        )
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        self.check_suggest(
            'login',
            {'login': login, 'firstname': firstname, 'lastname': lastname,
             'phone_number': '+79031234567', 'track_id': self.track_id},
            {'logins': []},
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'suggest_login_error',
                login=login,
                phone_number='+79031******',
                firstname=firstname,
                lastname=lastname,
                track_id=self.track_id,
            ),
        ])

    def test_suggest_login_statbox_logs_empty_login(self):
        firstname = 'firstname'
        lastname = 'lastname'
        self.env.login_suggester.setup_next_pack_side_effect([[]])
        self.check_suggest(
            'login',
            {'firstname': firstname, 'lastname': lastname,
             'phone_number': '+79031234567', 'track_id': self.track_id},
            {'logins': []},
        )
        self.env.statbox.assert_has_written([])

    def test_available_logins_only__not_yandex_ip(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['phne-free'],
            ['uid-free'],
            ['yandex-team-free'],
            ['yndx-free'],
            ['cassian'],
            [],
        ])

        self.env.blackbox.set_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'cassian': 'free'}),
        )
        self.check_suggest(
            'login',
            {'login': 'yndx-free'},
            {'logins': ['cassian']},
            headers=mock_headers(user_ip='8.8.8.8'),
        )
        self.env.blackbox.requests[-1].assert_query_contains({
            'logins': ['cassian'],
            'method': 'loginoccupation',
            'format': 'json',
        })

    def test_available_logins_only__yandex_ip(self):
        self.env.login_suggester.setup_next_pack_side_effect([
            ['phne-free', 'uid-free', 'yandex-team-free', 'yndx-free', 'yndx-occupied'],
            [],
        ])

        self.env.blackbox.set_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {
                    'yandex-team-free': 'free',
                    'yndx-free': 'free',
                    'yndx-occupied': 'occupied',
                },
            ),
        )

        self.check_suggest(
            'login',
            {'login': 'test'},
            {'logins': ['yandex-team-free', 'yndx-free']},
            headers=mock_headers(user_ip='37.9.101.188'),
        )
        self.env.statbox.assert_has_written([])
        self.env.blackbox.requests[-1].assert_query_contains({
            'logins': ['yandex-team-free,yndx-free,yndx-occupied'],
            'method': 'loginoccupation',
            'format': 'json',
        })

    def test_suggest_gender(self):
        self.check_suggest('gender', {'name': 'Adam Smith'}, {'gender': 'male'})

    def test_suggest_gender_track_counter(self):
        self.check_suggest('gender', {'name': 'Adam Smith', 'track_id': self.track_id}, {'gender': 'male'})
        self.check_suggest('gender', {'name': 'Adam1 Smith1', 'track_id': self.track_id}, {'gender': 'unknown'})
        self.check_suggest('gender', {'name': 'Adam2 Smith2', 'track_id': self.track_id}, {'gender': 'unknown'})
        eq_(self.track_manager.read(self.track_id).suggest_gender_count.get(), 3)

    def test_suggest_from_firstname(self):
        self.check_suggest('gender', {'firstname': 'Jane'}, {'gender': 'female'})

    def test_suggest_from_lastname(self):
        self.check_suggest('gender', {'lastname': u'Петрова'}, {'gender': 'female'})

    def test_suggest_from_lastname_and_firstname(self):
        self.check_suggest('gender', {'firstname': 'Adam', 'lastname': 'Smith'}, {'gender': 'male'})

    def test_suggest_gender_unknown(self):
        self.check_suggest('gender', {'name': 'fakedname'}, {'gender': 'unknown'})

    def test_suggest_country_unknown_country(self):
        self.check_suggest('country', {}, {'country': ['ru']},
                           headers=mock_headers(user_ip='127.0.0.1',
                                                host=''))

    def test_suggest_country_tr1(self):
        self.check_suggest('country', {}, {'country': ['tr']},
                           headers=mock_headers(host='passport.yandex.com.tr'))

    def test_suggest_country_tr2(self):
        self.check_suggest('country', {}, {'country': ['tr']},
                           headers=mock_headers(user_ip='144.122.145.170'))

    def test_suggest_country_tr3(self):
        self.check_suggest('country', {}, {'country': ['tr']},
                           headers=mock_headers(user_ip='144.122.145.170', host='passport.yandex.com.tr'))

    def test_suggest_country_us1(self):
        self.check_suggest('country', {}, {'country': ['us']},
                           headers=mock_headers(user_ip='8.8.8.8'))

    def test_suggest_country_us2(self):
        self.check_suggest('country', {}, {'country': ['us']},
                           headers=mock_headers(host='passport.yandex.com'))

    def test_suggest_country_tr_us(self):
        self.check_suggest('country', {}, {'country': ['tr', 'us']},
                           headers=mock_headers(user_ip='8.8.8.8', host='passport.yandex.com.tr'))

    def test_suggest_country_us_tr(self):
        self.check_suggest('country', {}, {'country': ['us', 'tr']},
                           headers=mock_headers(user_ip='144.122.145.170', host='yandex.com'))

    def test_suggest_country_track_counter(self):
        self.check_suggest('country', {'track_id': self.track_id}, {'country': ['us']},
                           headers=mock_headers(user_ip='8.8.8.8'))
        self.check_suggest('country', {'track_id': self.track_id}, {'country': ['us']},
                           headers=mock_headers(user_ip='8.8.8.8'))
        eq_(self.track_manager.read(self.track_id).suggest_country_count.get(), 2)

    def test_suggest_timezone_unknown_timezone(self):
        self.check_suggest('timezone', {}, {'timezone': []},
                           headers=mock_headers(user_ip='127.0.0.1'))

    def test_suggest_timezone_1(self):
        self.check_suggest('timezone', {}, {'timezone': ['Europe/Moscow']},
                           headers=mock_headers(user_ip='37.140.169.2'))

        self.check_suggest('country', {}, {'country': ['us']},
                           headers=mock_headers(user_ip='8.8.8.8'))

    def test_suggest_timezone_track_counter(self):
        self.check_suggest('timezone', {'track_id': self.track_id}, {'timezone': ['America/New_York']},
                           headers=mock_headers(user_ip='8.8.8.8'))
        self.check_suggest('timezone', {'track_id': self.track_id}, {'timezone': ['America/New_York']},
                           headers=mock_headers(user_ip='8.8.8.8'))
        eq_(self.track_manager.read(self.track_id).suggest_timezone_count.get(), 2)

    def test_suggest_language(self):
        self.check_suggest('language', {}, {'language': 'tr'},
                           headers=mock_headers(host='passport.yandex.com.tr', user_ip='144.122.145.170'))

    def test_suggest_language_cookiemy(self):
        self.check_suggest('language', {}, {'language': 'uk'},
                           headers=mock_headers(host='passport.yandex.ru',
                                                user_ip='213.180.195.32',
                                                cookie='my=%s' % cookiemy_for_language('uk')))

    def test_suggest_language_accept_language(self):
        self.check_suggest('language', {}, {'language': 'en'},
                           headers=mock_headers(host='passport.yandex.com',
                                                accept_language='ru'))

    def test_suggest_language_host_not_in_detect_languages(self):
        self.check_suggest('language', {}, {'language': 'en'},
                           headers=mock_headers(host='abrakadabra'))

    def test_suggest_language_omit_host_header(self):
        rv = self.env.client.post('/1/suggest/language/?consumer=dev', headers=mock_headers(host=''))
        eq_(rv.status_code, 400)
        assert_errors(json.loads(rv.data)['errors'], {None: 'missingheader'})

    def test_suggest_timezone_omit_host_header(self):
        rv = self.env.client.post('/1/suggest/timezone/?consumer=dev', headers=mock_headers(host=''))
        eq_(rv.status_code, 400)
        assert_errors(json.loads(rv.data)['errors'], {None: 'missingheader'})

    def test_suggest_language_track_counter(self):
        self.check_suggest('language', {'track_id': self.track_id}, {'language': 'en'},
                           headers=mock_headers(host='passport.yandex.com',
                                                accept_language='ru'))
        self.check_suggest('language', {'track_id': self.track_id}, {'language': 'en'},
                           headers=mock_headers(host='passport.yandex.com',
                                                accept_language='ru'))
        eq_(self.track_manager.read(self.track_id).suggest_language_count.get(), 2)


class _TranslationSettings(object):
    QUESTIONS = {
        'ru': {
            '0': 'не выбран',
            '1': 'Первый вопрос',
            '2': 'filtered',
        },
    }

    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


@with_settings_hosts(
    DISPLAY_LANGUAGES=['ru'],
    HINT_QUESTION_IDS_FOR_LANGUAGES={
        'ru': ['0', '1'],
    },
    translations=_TranslationSettings,
)
class TestControlQuestions(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'control_questions': ['*']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def control_question_request(self, data):
        return self.env.client.post('/1/questions/?consumer=dev', data=data)

    def test_good(self):
        for language, hint_question_id_range in settings.HINT_QUESTION_IDS_FOR_LANGUAGES.items():
            rv = self.control_question_request({'display_language': language})
            eq_(rv.status_code, 200)

            resp = json.loads(rv.data)
            ok_('questions' in resp)

            eq_(resp['questions'], [{'id': '0', 'value': u'не выбран'},
                                    {'id': '1', 'value': u'Первый вопрос'}])

    def test_bad(self):
        rv = self.control_question_request({'display_language': 'blablabla'})
        eq_(rv.status_code, 400)

    def test_track_counter(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'control_questions': ['*'], 'track': ['update']}))
        self.control_question_request({'display_language': 'ru', 'track_id': self.track_id})
        self.control_question_request({'display_language': 'ru', 'track_id': self.track_id})
        eq_(self.track_manager.read(self.track_id).control_questions_count.get(), 2)
