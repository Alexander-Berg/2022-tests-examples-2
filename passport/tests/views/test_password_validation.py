# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(BASIC_PASSWORD_POLICY_MIN_QUALITY=10)
class TestPasswordValidation(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'password': ['validate']}))
        self.setup_shakur_responses()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'password_validation_error',
            track_id=self.track_id,
            action='password_validation_error',
            weak='1',
            password_quality='4',
            length='6',
            classes_number='1',
            sequences_number='0',
            is_sequence='0',
            is_word='0',
            is_additional_word='0',
            additional_subwords_number='0',
        )

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def password_validation_request(self, data):
        return self.env.client.post('/1/validation/password/?consumer=dev', data=data)

    def test_ok(self):
        rv = self.password_validation_request({
            'login': 'invisible',
            'password': 'aaa1bbbccc',
        })
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok'})

    def test_track_counter(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'password': ['validate'], 'track': ['update']}))
        self.password_validation_request({
            'login': 'invisible',
            'password': 'aaa1bbbccc',
            'track_id': self.track_id,
        })
        self.password_validation_request({
            'login': 'invisible',
            'password': 'aaa1bbbccc',
            'track_id': self.track_id,
        })
        track = self.track_manager.read(self.track_id)
        eq_(track.password_validation_count.get(), 2)

    def test_track_timings(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'password': ['validate'], 'track': ['update']}))
        args = {
            'login': 'invisible',
            'password': 'aaa1bbbccc',
            'track_id': self.track_id,
        }

        self.password_validation_request(args)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            eq_(track.password_validation_first_call, TimeNow())
            eq_(track.password_validation_last_call, TimeNow())
            track.password_validation_first_call = 123

        self.password_validation_request(args)
        track = self.track_manager.read(self.track_id)
        eq_(track.password_validation_first_call, '123')
        eq_(track.password_validation_last_call, TimeNow())

    def test_weak_warning(self):
        rv = self.password_validation_request({
            'login': 'under',
            'password': 'aaabbbcdef',
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_warnings'], {'password': 'weak'})

    def test_weak_error(self):
        rv = self.password_validation_request({
            'login': 'under',
            'password': 'aaabbb',
            'track_id': self.track_id,
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'password': 'weak'})
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('password_validation_error'),
        ])

    def test_password_error(self):
        rv = self.password_validation_request({
            'login': 'under',
            'password': 'olya',
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'password': 'tooshort'})

    def test_weak_password_with_strong_policy(self):
        rv = self.password_validation_request({
            'login': 'under',
            'password': '1234512345',
            'policy': 'strong',
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'password': 'weak'})

    def test_weak_password_with_strong_policy_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True
        rv = self.password_validation_request({
            'login': 'under',
            'password': '1234512345',
            'track_id': self.track_id,
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'password': 'weak'})

    def test_password_with_strong_policy_from_track_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True
        rv = self.password_validation_request({
            'login': 'under',
            'password': 'strong_password1234',
            'track_id': self.track_id,
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)
        eq_(self.env.blackbox.get_requests_by_method('pwdhistory'), [])

    def test_password_tooshort(self):
        rv = self.password_validation_request({
            'login': 'under',
            'password': 'foobar123',
            'policy': 'strong',
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], [{'password': 'tooshort'}])

    def test_password_eq_login(self):
        rv = self.password_validation_request({
            'login': 'foobar',
            'password': 'foobar',
        })
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], [{'password': 'likelogin'}])

    def test_password_eq_login_from_track(self):
        args = {
            'password': 'foobar',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = 'foobar'
        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], [{'password': 'likelogin'}])

    def test_password_eq_old_password_ok(self):
        """В ручке валидации не смотрим на хеш старого пароля в треке, не смотрим в историю паролей"""
        args = {
            'login': 'invisible',
            'password': 'foobar',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.password_hash = '$1$nbPtTWDF$VJSRhPcGQ8TBzyzSFS83O1'
        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)
        eq_(self.env.blackbox.get_requests_by_method('pwdhistory'), [])

    def test_password_like_email_ok(self):
        """В ручке валидации не смотрим на email-ы в треке"""
        args = {
            'login': 'invisible',
            'password': 'invisible@yandex.ru',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.emails = 'invisible@yandex.ru invisible@yandex.com'

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_like_default_email_ok(self):
        """В ручке валидации не смотрим на email-ы по умолчанию"""
        args = {
            'login': 'invisible',
            'password': 'invisible@yandex.ru',
            'track_id': self.track_id,
        }

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_like_phone_user_with_confirmed_secure_number_ok(self):
        """В ручке валидации не смотрим на телефоны в треке"""
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = '+79261234567'
            track.phone_confirmation_is_confirmed = True
            track.country = 'ru'

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_like_phone_user_with_secure_number_in_yasms_ok(self):
        """В ручке валидации не смотрим на телефоны в треке"""
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.secure_phone_number = '+79261234567'
            track.can_use_secure_number_for_password_validation = True
            track.country = 'ru'

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_with_not_confirmed_number(self):
        """В ручке валидации не смотрим на телефоны в треке"""
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'track_id': self.track_id,
        }
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = '+79261234567'
            track.country = 'ru'

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_like_phone_number_in_form(self):
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'phone_number': '+79261234567',
            'track_id': self.track_id,
        }

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], [{'password': 'likephonenumber'}])

    def test_password_like_phone_number_in_form_country_unknown(self):
        """Информации о стране нет, не можем сравнить пароль с телефонным номером"""
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'phone_number': '89261234567',
            'track_id': self.track_id,
        }

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        ok_('validation_errors' not in response)

    def test_password_like_phone_number_in_form_with_country(self):
        """Информация о стране передана в форме, можем проверить совпадение пароля с телефоном"""
        args = {
            'login': 'invisible',
            'password': '8(926)123-45-67',
            'phone_number': '89261234567',
            'country': 'ru',
            'track_id': self.track_id,
        }

        rv = self.password_validation_request(args)
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], [{'password': 'likephonenumber'}])
