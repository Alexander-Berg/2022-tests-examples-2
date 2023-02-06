# -*- coding: utf-8 -*-
import mock
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    reg_country_city_factors,
    reg_country_city_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_response,
)
from passport.backend.core.compare.compare import (
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_INEXACT_MATCH,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class RegistrationCountryCityHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def setUp(self):
        super(RegistrationCountryCityHandlerTestCase, self).setUp()

        self.region_mock = mock.Mock(
            country=dict(id=TEST_REGISTRATION_COUNTRY_ID, en_name=u'Russia', short_en_name=u'RU'),
            city=dict(id=TEST_REGISTRATION_CITY_ID, en_name=u'Moscow', short_en_name=u''),
        )
        self.region_mock.country['name'] = TEST_DEFAULT_REGISTRATION_COUNTRY.encode('utf-8')
        self.region_mock.city['name'] = TEST_REGISTRATION_CITY.encode('utf-8')

    def tearDown(self):
        del self.region_mock
        super(RegistrationCountryCityHandlerTestCase, self).tearDown()

    def form_values(
        self,
        registration_country=TEST_DEFAULT_REGISTRATION_COUNTRY,
        registration_country_id=None,
        registration_city=None,
        registration_city_id=None
    ):
        values = {
            'registration_country': registration_country,
            'registration_country_id': registration_country_id,
            'registration_city': registration_city,
            'registration_city_id': registration_city_id,
        }
        return values

    def test_registration_country_match(self):
        """Совпадение страны регистрации. По каким-то причинам на фронте не удалось получить ID геобазы."""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name='userinfo_ft', user_ip=TEST_IP)]),
        )
        form_values = self.form_values(registration_country=u'RU')  # Совпадение по short_en_name
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: self.region_mock):
                factors = view.calculate_factors('reg_country_city')

            eq_(
                factors,
                reg_country_city_factors(
                    registration_ip=TEST_IP,
                    registration_country_entered=u'RU',
                    registration_country_entered_id=None,
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor=STRING_FACTOR_NO_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_history=TEST_REGISTRATION_CITY,
                    registration_city_history_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
                    registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
                ),
            )
            self.assert_entry_in_statbox(
                reg_country_city_statbox_entry(
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor=STRING_FACTOR_NO_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_registration_country_id_match(self):
        """Совпадение ID страны регистрации"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name='userinfo_ft', user_ip=TEST_IP)]),
        )
        form_values = self.form_values(
            registration_country=TEST_DEFAULT_REGISTRATION_COUNTRY,
            registration_country_id=TEST_REGISTRATION_COUNTRY_ID,
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: self.region_mock):
                factors = view.calculate_factors('reg_country_city')

            eq_(
                factors,
                reg_country_city_factors(
                    registration_ip=TEST_IP,
                    registration_country_entered_id=TEST_REGISTRATION_COUNTRY_ID,
                    registration_country_factor_id=FACTOR_BOOL_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor=STRING_FACTOR_NO_MATCH,
                    registration_city_history=TEST_REGISTRATION_CITY,
                    registration_city_history_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
                    registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
                ),
            )
            self.assert_entry_in_statbox(
                reg_country_city_statbox_entry(
                    registration_country_factor_id=FACTOR_BOOL_MATCH,
                    registration_city_factor=STRING_FACTOR_NO_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_registration_city_match(self):
        """Совпадение города регистрации"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name='action', value='account_register_simple', user_ip=TEST_IP)]),
        )
        form_values = self.form_values(registration_city=u'Moscoww')  # Неточное совпадение по ename
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: self.region_mock):
                factors = view.calculate_factors('reg_country_city')

            eq_(
                factors,
                reg_country_city_factors(
                    registration_ip=TEST_IP,
                    registration_city_entered=u'Moscoww',
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor=STRING_FACTOR_INEXACT_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_history=TEST_REGISTRATION_CITY,
                    registration_city_history_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
                    registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
                ),
            )
            self.assert_entry_in_statbox(
                reg_country_city_statbox_entry(
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor=STRING_FACTOR_INEXACT_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )

    def test_registration_city_id_match(self):
        """Совпадение ID города регистрации"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name='action', value='account_create', user_ip=TEST_IP)]),
        )
        form_values = self.form_values(
            registration_city=u'Москва',
            registration_city_id=TEST_REGISTRATION_CITY_ID,
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: self.region_mock):
                factors = view.calculate_factors('reg_country_city')

            eq_(
                factors,
                reg_country_city_factors(
                    registration_ip=TEST_IP,
                    registration_city_entered=u'Москва',
                    registration_city_entered_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_MATCH,
                    registration_city_history=TEST_REGISTRATION_CITY,
                    registration_city_history_id=TEST_REGISTRATION_CITY_ID,
                    registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
                    registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
                ),
            )
            self.assert_entry_in_statbox(
                reg_country_city_statbox_entry(
                    registration_country_factor=STRING_FACTOR_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor_id=FACTOR_BOOL_MATCH,
                ),
                view.statbox,
            )

    def test_registration_city_not_in_geobase(self):
        """Геобаза по IP регистрации нашла только страну"""
        IP_WITHOUT_CITY = '59.154.99.143'
        region_mock = mock.Mock(
            country=dict(id=211, en_name=u'Australia', short_en_name=u'AU'),
            city=None,
        )
        region_mock.country['name'] = u'Австралия'.encode('utf-8')

        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name='action', value='account_create', user_ip=IP_WITHOUT_CITY)]),
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            with mock.patch('passport.backend.core.geobase.Region', lambda ip=None, geobase=None: region_mock):
                factors = view.calculate_factors('reg_country_city')

            eq_(
                factors,
                reg_country_city_factors(
                    registration_ip=IP_WITHOUT_CITY,
                    registration_country_history_id=211,
                    registration_country_history=u'Австралия',
                    registration_country_factor=STRING_FACTOR_NO_MATCH,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                    registration_city_factor_id=FACTOR_NOT_SET,
                    registration_city_history_id=None,
                    registration_city_history=None,
                ),
            )
            self.assert_entry_in_statbox(
                reg_country_city_statbox_entry(
                    registration_country_factor=STRING_FACTOR_NO_MATCH,
                    registration_city_factor_id=FACTOR_NOT_SET,
                    registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
                ),
                view.statbox,
            )
