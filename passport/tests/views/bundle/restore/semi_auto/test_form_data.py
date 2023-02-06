# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import (
    BaseTestRestoreSemiAutoView,
    CheckAccountByLoginTests,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_DEFAULT_HINT_QUESTION,
    TEST_DEFAULT_HINT_QUESTION_TEXT,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_UID,
    TEST_EMAILS_IN_TRACK,
    TEST_IP,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PDD_DOMAIN,
    TEST_PDD_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_response,
)
from passport.backend.core.counters import restore_semi_auto_compare_counter
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_RETRIES=1,
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
)
class TestRestoreSemiAutoFormDataView(CheckAccountByLoginTests, BaseTestRestoreSemiAutoView):
    def setUp(self):
        super(TestRestoreSemiAutoFormDataView, self).setUp()
        self.default_url = '/1/bundle/restore/semi_auto/form_data/'
        self.set_track_values()

    def tearDown(self):
        super(TestRestoreSemiAutoFormDataView, self).tearDown()

    def setup_statbox_templates(self):
        super(TestRestoreSemiAutoFormDataView, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            action='form_data_requested',
            _exclude=['uid'],
        )

    def query_params(self):
        return {}

    def make_request(self, data=None, headers=None):
        data = data or {}
        data['consumer'] = 'dev'
        data['track_id'] = self.track_id
        return self.env.client.get(
            self.default_url,
            query_string=data,
            headers=headers,
        )

    def make_post_request(self, headers=None):
        return self.env.client.post(
            self.default_url + '?consumer=dev',
            data={'track_id': self.track_id},
            headers=headers,
        )

    def set_track_values(self, user_entered_login=TEST_DEFAULT_LOGIN, **params):
        params['user_entered_login'] = user_entered_login
        params['request_source'] = 'restore'
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for attr_name, value in params.items():
                setattr(track, attr_name, value)
            self.orig_track = track.snapshot()

    def assert_track_updated(self, questions, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                             emails=TEST_EMAILS_IN_TRACK, domain=None):
        orig_track_data = self.orig_track._data
        orig_track_data.update(questions=json.dumps(questions), uid=str(uid), login=login, country='ru', emails=emails)
        if domain is not None:
            orig_track_data.update(domain=domain)
        track = self.track_manager.read(self.track_id)
        new_track_data = track._data
        eq_(orig_track_data, new_track_data)

    def test_ip_limit_exceeded_fails(self):
        """В ручке commit переполнен счетчик по IP"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        counter = restore_semi_auto_compare_counter.get_per_ip_buckets()
        # установим счетчик вызовов на ip в limit
        for i in range(counter.limit + 1):
            counter.incr(TEST_IP)

        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('finished_with_state', state='rate_limit_exceeded'),
        ])
        self.assert_track_unchanged()

    def test_uid_limit_exceeded_fails(self):
        """В ручке commit переполнен счетчик по UID"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        counter = restore_semi_auto_compare_counter.get_per_uid_buckets()
        # установим счетчик вызовов на uid в limit
        for i in range(counter.limit + 1):
            counter.incr(TEST_DEFAULT_UID)

        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, state='rate_limit_exceeded')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('finished_with_state', state='rate_limit_exceeded'),
        ])
        self.assert_track_unchanged()

    def test_autoregistered_password_changing_required_redirect(self):
        """Автозарегистрированный пользователь с требованием смены пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password_creating_required=True, subscribed_to=[100]),
        )
        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, state='complete_autoregistered')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('finished_with_state', state='complete_autoregistered'),
        ])
        self.assert_track_unchanged()

    def test_pdd_cyrillic_domain_served_ok(self):
        """ПДД-пользователь с кириллическим доменом, обслуживается саппортом Яндекса"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_CYRILLIC_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_CYRILLIC_LOGIN,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_CYRILLIC_DOMAIN,
            ),
        )
        resp = self.make_request(headers=self.get_headers())

        self.assert_ok_response(resp, questions=[{'id': 0, 'text': TEST_DEFAULT_HINT_QUESTION_TEXT}])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        self.assert_track_updated(
            questions=[{'id': 99, 'text': TEST_DEFAULT_HINT_QUESTION_TEXT}],
            login=TEST_PDD_CYRILLIC_LOGIN,
            uid=TEST_PDD_UID,
            domain=TEST_PDD_CYRILLIC_DOMAIN,
        )

    def test_post_request_works(self):
        """Поддерживаем также POST-запрос"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name='info.hintq', value=TEST_DEFAULT_HINT_QUESTION),
            ]),
        )
        resp = self.make_post_request(headers=self.get_headers())

        self.assert_ok_response(
            resp,
            questions=[{'id': 0, 'text': 'question'}],
        )
        self.assert_track_updated(
            questions=[{'id': 99, 'text': 'question'}],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
