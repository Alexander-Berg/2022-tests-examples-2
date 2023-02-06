# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import (
    BaseTestMultiStepWithCommitUtils,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_LASTNAME,
    TEST_DELIVERY_ADDRESS_1,
    TEST_DELIVERY_ADDRESS_2,
    TEST_SOCIAL_LINK,
)
from passport.backend.api.views.bundle.restore.semi_auto.helpers import (
    _format_delivery_addresses,
    _format_social_accounts,
    FEATURE_NOT_CALCULATED_VALUE,
    get_features_from_factors,
)
from passport.backend.core.builders.social_api.faker.social_api import task_data_response
from passport.backend.core.compare import (
    BIRTHDAYS_FACTOR_FULL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    STRING_FACTOR_MATCH,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings,
    with_settings_hosts,
)
from passport.backend.utils.file import read_file


eq_ = iterdiff(eq_)


@with_settings()
class FormatDeliveryAddressesTestCase(unittest.TestCase):

    def test_with_empty_addresses(self):
        eq_(_format_delivery_addresses([], 'ru'), [])

    def test_with_single_address(self):
        eq_(
            _format_delivery_addresses([TEST_DELIVERY_ADDRESS_1], 'ru'),
            u'Страна: Россия, Город: moscow, Улица: tolstoy, Дом: 16',
        )
        eq_(
            _format_delivery_addresses([TEST_DELIVERY_ADDRESS_1], 'tr'),
            u'Ülke: Россия, Şehir: moscow, Sokak: tolstoy, Ev: 16',
        )

    def test_with_multiple_addresses(self):
        eq_(
            _format_delivery_addresses([TEST_DELIVERY_ADDRESS_1, TEST_DELIVERY_ADDRESS_2], 'en'),
            u'Country: Россия, City: moscow, Street: tolstoy, House: 16; Country: rf, City: Иваново, Street: tolstoy, House: 16, Corpus / Bldg.: 10c4',
        )


class FormatSocialAccountsTestCase(unittest.TestCase):

    def test_with_full_info(self):
        account_info = task_data_response(
            firstname=TEST_DEFAULT_FIRSTNAME,
            lastname=TEST_DEFAULT_LASTNAME,
            links=[TEST_SOCIAL_LINK],
        )['profile']

        eq_(
            _format_social_accounts([account_info]),
            '%s %s (%s)' % (
                TEST_DEFAULT_FIRSTNAME,
                TEST_DEFAULT_LASTNAME,
                TEST_SOCIAL_LINK,
            ),
        )

    def test_with_firstname_only(self):
        account_info = task_data_response(
            firstname=TEST_DEFAULT_FIRSTNAME,
            lastname=None,
            links=[],
            provider_name='facebook',
        )['profile']

        eq_(
            _format_social_accounts([account_info]),
            '%s (Facebook)' % TEST_DEFAULT_FIRSTNAME,
        )

    def test_with_link_only(self):
        account_info = task_data_response(
            firstname=None,
            lastname=None,
            links=[TEST_SOCIAL_LINK],
        )['profile']

        eq_(
            _format_social_accounts([account_info]),
            TEST_SOCIAL_LINK,
        )

    def test_with_no_info(self):
        """Известно только название соц. сети"""
        account_info = task_data_response(
            firstname=None,
            lastname=None,
            links=[],
            provider_name='linkedin',
        )['profile']

        eq_(
            _format_social_accounts([account_info]),
            'Linkedin',
        )

    def test_with_multiple_accounts(self):
        account_info_1 = task_data_response(
            firstname=None,
            lastname=None,
            links=[],
            provider_name='linkedin',
        )['profile']
        account_info_2 = task_data_response(
            firstname=TEST_DEFAULT_FIRSTNAME,
            lastname=TEST_DEFAULT_LASTNAME,
            links=[TEST_SOCIAL_LINK],
        )['profile']

        eq_(
            _format_social_accounts([account_info_1, account_info_2]),
            'Linkedin, %s %s (%s)' % (
                TEST_DEFAULT_FIRSTNAME,
                TEST_DEFAULT_LASTNAME,
                TEST_SOCIAL_LINK,
            ),
        )


@with_settings_hosts()
class GetFeaturesFromFactorsTestCase(BaseTestMultiStepWithCommitUtils):
    def test_get_features_from_factors(self):
        """Базовый тест на получение преобразованных значений факторов для передачи в TensorNet"""
        factors = self.make_step_3_factors(self.make_step_2_factors(self.make_step_1_factors(is_for_learning=True)))
        factors = self.make_step_6_factors(self.make_step_5_factors(self.make_step_4_factors(factors)))
        allowed_features = read_file(settings.RESTORE_SEMI_AUTO_FEATURES_FILE).strip().split()
        map = {feature: index for index, feature in enumerate(allowed_features)}

        features = get_features_from_factors(factors)

        features_values = (
            ('aggregated_password_and_personal_change_one_day_ip_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ip_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ip_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ip_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_password_and_personal_change_one_day_subnet_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_subnet_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_subnet_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_subnet_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_password_and_personal_change_one_day_ua_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ua_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_personal_change_one_day_ua_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_password_and_recovery_change_one_day_ip_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ip_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ip_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ip_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_password_and_recovery_change_one_day_subnet_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_subnet_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_subnet_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_subnet_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_password_and_recovery_change_one_day_ua_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ua_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_password_and_recovery_change_one_day_ua_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_personal_and_recovery_change_one_day_ip_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_ip_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_ip_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_personal_and_recovery_change_one_day_subnet_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_subnet_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_subnet_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_personal_and_recovery_change_one_day_ua_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_ua_eq_user', FEATURE_NOT_CALCULATED_VALUE),
            ('aggregated_personal_and_recovery_change_one_day_ua_match', FACTOR_BOOL_NO_MATCH),
            ('aggregated_personal_and_recovery_change_one_day_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_best', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_depth_2', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ip_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ip_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_subnet_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_subnet_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ua_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_change_ua_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_current', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ip_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ip_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ip_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_subnet_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_subnet_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_subnet_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ua_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ua_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ua_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('answer_match_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_depth_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ip_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ip_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ip_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_subnet_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_subnet_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_subnet_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ua_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ua_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_change_ua_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_current', BIRTHDAYS_FACTOR_FULL_MATCH),
            ('birthday_intermediate', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_intermediate_depth', FEATURE_NOT_CALCULATED_VALUE),
            ('birthday_registration', BIRTHDAYS_FACTOR_FULL_MATCH),
            ('delivery_addresses_has_matches', FACTOR_BOOL_NO_MATCH),
            ('email_blacklist_has_matches', FACTOR_BOOL_NO_MATCH),
            ('email_collectors_has_matches', FACTOR_BOOL_NO_MATCH),
            ('email_folders_has_matches', FACTOR_BOOL_NO_MATCH),
            ('email_whitelist_has_matches', FACTOR_BOOL_NO_MATCH),
            ('emails_has_matches', FACTOR_BOOL_NO_MATCH),
            ('names_change_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_depth_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ip_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_subnet_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_reg_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_change_ua_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('names_current_0', STRING_FACTOR_MATCH),
            ('names_current_1', STRING_FACTOR_MATCH),
            ('names_intermediate_0', FEATURE_NOT_CALCULATED_VALUE),
            ('names_intermediate_1', FEATURE_NOT_CALCULATED_VALUE),
            ('names_intermediate_depth', FEATURE_NOT_CALCULATED_VALUE),
            ('names_registration_0', STRING_FACTOR_MATCH),
            ('names_registration_1', STRING_FACTOR_MATCH),
            ('outbound_emails_has_matches', FACTOR_BOOL_NO_MATCH),
            ('passwords_auth_date_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_auth_date_1', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_auth_date_2', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_auth_found_0', FACTOR_BOOL_NO_MATCH),
            ('passwords_auth_found_1', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_auth_found_2', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_change_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_first_auth_depth_2', FEATURE_NOT_CALCULATED_VALUE),
            ('passwords_forced_change_pending', FACTOR_BOOL_NO_MATCH),
            ('passwords_last_change_is_forced_change', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_depth_2', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ip_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ip_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_subnet_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_subnet_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ua_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_change_ua_eq_user_2', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_has_matches', FACTOR_BOOL_NO_MATCH),
            ('phone_numbers_match_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ip_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_subnet_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_eq_reg_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_eq_reg_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_eq_user_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_eq_user_1', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_first_auth_depth_0', FEATURE_NOT_CALCULATED_VALUE),
            ('phone_numbers_match_ua_first_auth_depth_1', FEATURE_NOT_CALCULATED_VALUE),
            ('registration_city_id', FEATURE_NOT_CALCULATED_VALUE),
            ('registration_city_text', FEATURE_NOT_CALCULATED_VALUE),
            ('registration_country_id', FEATURE_NOT_CALCULATED_VALUE),
            ('registration_country_text', FEATURE_NOT_CALCULATED_VALUE),
            ('registration_date', FACTOR_FLOAT_MATCH),
            ('services_has_matches', FACTOR_BOOL_NO_MATCH),
            ('social_accounts_has_matches', FACTOR_BOOL_NO_MATCH),
            ('user_env_auths_auths_limit_reached', FACTOR_BOOL_NO_MATCH),
            ('user_env_auths_ip_auth_interval', FACTOR_FLOAT_NO_MATCH),
            ('user_env_auths_ip_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('user_env_auths_ip_first_auth_depth', FACTOR_FLOAT_MATCH),
            ('user_env_auths_subnet_auth_interval', FACTOR_FLOAT_NO_MATCH),
            ('user_env_auths_subnet_eq_reg', FEATURE_NOT_CALCULATED_VALUE),
            ('user_env_auths_subnet_first_auth_depth', FACTOR_FLOAT_MATCH),
            ('user_env_auths_ua_auth_interval', FEATURE_NOT_CALCULATED_VALUE),
            ('user_env_auths_ua_eq_reg', FACTOR_BOOL_NO_MATCH),
            ('user_env_auths_ua_first_auth_depth', FEATURE_NOT_CALCULATED_VALUE),
        )

        eq_(len(features_values), len(features))
        for feature_name, expected_value in features_values:
            value = features[map[feature_name]]
            eq_(value, expected_value)
