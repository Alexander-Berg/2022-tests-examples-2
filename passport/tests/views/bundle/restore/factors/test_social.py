# -*- coding: utf-8 -*-
from nose.tools import raises
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    social_factors,
    social_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.core.builders.social_api import BaseSocialApiError
from passport.backend.core.builders.social_api.faker.social_api import (
    EXISTING_USERID,
    FACEBOOK_BUSINESS_ID,
    FACEBOOK_BUSINESS_TOKEN,
    GOOGLE_PROVIDER,
    profile_item,
    task_data_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts(
    SOCIAL_API_URL='http://social.localhost/api/',
)
class SocialAccountsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, social_accounts=None):
        return {
            'social_accounts': social_accounts if social_accounts is not None else [TEST_SOCIAL_TASK_ID],
        }

    def assert_social_api_called(self, task_ids=None, user_ids=None):
        task_ids = [TEST_SOCIAL_TASK_ID] if task_ids is None else task_ids
        user_ids = [EXISTING_USERID] if user_ids is None else user_ids
        requests = self.env.social_api.requests
        # вызов profiles для поиска привязанных к аккаунту профилей
        requests[0].assert_url_starts_with('http://social.localhost/api/user/1/profile')
        requests[0].assert_query_equals(
            {
                'include': 'person',
                'consumer': 'passport',
            },
        )
        index = 1

        for task_id in task_ids:
            # получение данных по task_id
            requests[index].assert_url_starts_with('http://social.localhost/api/task/%s' % task_id)
            index += 1

        user_ids_found = set()
        for user_id in user_ids:
            # получение профиля для task_id
            requests[index].assert_url_starts_with('http://social.localhost/api/profiles')
            requests[index].assert_query_contains({'include': 'person'})
            query_params = requests[index].get_query_params()
            user_ids_found.add(query_params['userid'][0])
            index += 1
        eq_(set(user_ids), user_ids_found)

    def test_no_account_profiles_no_entered_profiles(self):
        """Нет введенных профилей, нет привязанных профилей"""
        userinfo_response = self.default_userinfo_response()
        self.env.social_api.set_social_api_response_value(dict(profiles=[]))
        form_values = self.form_values(social_accounts=[])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            eq_(factors, social_factors())
            self.assert_entry_in_statbox(social_statbox_entry(), view.statbox)
            self.assert_social_api_called(task_ids=[], user_ids=[])

    def test_with_account_profiles_no_entered_profiles(self):
        """Нет введенных профилей, есть привязанные профили"""
        userinfo_response = self.default_userinfo_response()
        self.env.social_api.set_social_api_response_value(dict(profiles=[
            profile_item(),
        ]))
        form_values = self.form_values(social_accounts=[])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_account_profiles=[profile_item()],
                social_accounts_factor_account_profiles_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_account_profiles_count=1,
                ),
                view.statbox,
            )
            self.assert_social_api_called(task_ids=[], user_ids=[])

    def test_no_account_profiles_with_entered_not_bound_profile(self):
        """Есть введенные профили, не привязанные к Яндексу, нет привязанных к аккаунту профилей"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(TEST_TRACK_ID, task_id=TEST_SOCIAL_TASK_ID)
        self.env.social_api.set_social_api_response_side_effect([
            dict(profiles=[]),  # вызов profiles для поиска привязанных к аккаунту профилей
            task_data,  # получение данных по task_id
            dict(profiles=[]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_factor_entered_profiles_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_factor_entered_profiles_count=0,
                ),
                view.statbox,
            )
            self.assert_social_api_called()

    def test_task_with_business_info(self):
        """Есть введенный профиль, в нем присутствует business_info.
        Проверим, что нужные business данные ушли в social-api"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(TEST_TRACK_ID, task_id=TEST_SOCIAL_TASK_ID, with_business=True)
        self.env.social_api.set_social_api_response_side_effect([
            dict(profiles=[]),  # вызов profiles для поиска привязанных к аккаунту профилей
            task_data,
            dict(profiles=[]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_factor_entered_profiles_count=0,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_factor_entered_profiles_count=0,
                ),
                view.statbox,
            )
            self.assert_social_api_called()
            request = self.env.social_api.requests[2]
            request.assert_url_starts_with('http://social.localhost/api/profiles')
            request.assert_query_equals({
                'consumer': 'passport',
                'include': 'person',
                'userid': EXISTING_USERID,
                'business_token': FACEBOOK_BUSINESS_TOKEN,
                'business_id': str(FACEBOOK_BUSINESS_ID),
                'provider_id': str(GOOGLE_PROVIDER['id']),
            })

    @raises(ValueError)
    def test_task_with_broken_business_info(self):
        """Есть введенный профиль, в нем присутствует business_info, но в данных не хватает поля"""
        userinfo_response = self.default_userinfo_response()

        task_response = task_data_response(TEST_TRACK_ID, task_id=TEST_SOCIAL_TASK_ID, with_business=True)
        # Покалечим business в ответе
        del task_response['profile']['business']['id']

        self.env.social_api.set_social_api_response_side_effect([
            dict(profiles=[]),  # вызов profiles для поиска привязанных к аккаунту профилей
            task_response,
            dict(profiles=[]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            view.calculate_factors('social_accounts')

    def test_no_account_profiles_with_entered_bound_profile(self):
        """Есть введенные профили, привязанные к Яндексу, нет привязанных к аккаунту профилей"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        self.env.social_api.set_social_api_response_side_effect([
            dict(profiles=[]),  # вызов profiles для поиска привязанных к аккаунту профилей
            task_data,  # получение данных по task_id
            dict(profiles=[profile_item(uid=TEST_PDD_UID)]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_entered_profiles=[profile_item(uid=TEST_PDD_UID)],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_factor_entered_profiles_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_factor_entered_profiles_count=1,
                ),
                view.statbox,
            )
            self.assert_social_api_called()

    def test_with_account_profiles_with_entered_bound_profile_no_match(self):
        """Есть введенные профили, привязанные к Яндексу, есть привязанные к аккаунту профили, нет совпадения"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        self.env.social_api.set_social_api_response_side_effect([
            # вызов profiles для поиска привязанных к аккаунту профилей
            dict(profiles=[profile_item(profile_id=1), profile_item(profile_id=2)]),
            task_data,  # получение данных по task_id
            dict(profiles=[profile_item(uid=TEST_PDD_UID)]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_entered_profiles=[profile_item(uid=TEST_PDD_UID)],
                social_accounts_account_profiles=[profile_item(profile_id=1), profile_item(profile_id=2)],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_factor_entered_profiles_count=1,
                social_accounts_factor_account_profiles_count=2,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_factor_entered_profiles_count=1,
                    social_accounts_factor_account_profiles_count=2,
                ),
                view.statbox,
            )
            self.assert_social_api_called()

    def test_no_account_profiles_entered_duplicate_profiles_filtered(self):
        """Есть введенные профили-дубликаты, привязанные к Яндексу, нет привязанных к аккаунту профилей"""
        userinfo_response = self.default_userinfo_response()
        task_data_1 = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        task_data_2 = task_data_response(userid='123', task_id=TEST_SOCIAL_TASK_ID_2)
        task_data_3 = task_data_response(task_id=TEST_SOCIAL_TASK_ID_3)
        self.env.social_api.set_social_api_response_side_effect([
            # вызов profiles для поиска привязанных к аккаунту профилей
            dict(profiles=[]),
            task_data_1,  # получение данных по task_id
            task_data_2,  # получение данных по task_id
            task_data_3,  # получение данных по task_id - дубликат
            # получение профилей для первой пары провайдер, userid
            dict(profiles=[profile_item(profile_id=1, uid=TEST_PDD_UID)]),
            # получение профилей для второй пары провайдер, userid
            dict(profiles=[profile_item(profile_id=2, uid=TEST_PDD_UID)]),
        ])
        form_values = self.form_values(social_accounts=[
            TEST_SOCIAL_TASK_ID,
            TEST_SOCIAL_TASK_ID_2,
            TEST_SOCIAL_TASK_ID_3,
        ])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[
                    task_data_1['profile'],
                    task_data_2['profile'],
                    task_data_3['profile'],
                ],
                social_accounts_entered_profiles=[
                    profile_item(profile_id=1, uid=TEST_PDD_UID),
                    profile_item(profile_id=2, uid=TEST_PDD_UID),
                ],
                social_accounts_factor_entered_accounts_count=3,
                social_accounts_factor_entered_profiles_count=2,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=3,
                    social_accounts_factor_entered_profiles_count=2,
                ),
                view.statbox,
            )
            self.assert_social_api_called(
                task_ids=[TEST_SOCIAL_TASK_ID, TEST_SOCIAL_TASK_ID_2, TEST_SOCIAL_TASK_ID_3],
                user_ids=[EXISTING_USERID, '123'],
            )

    def test_with_account_profiles_with_entered_bound_profile_match(self):
        """Есть введенные профили, привязанные к Яндексу, есть привязанные к аккаунту профили, есть совпадения"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        self.env.social_api.set_social_api_response_side_effect([
            # вызов profiles для поиска привязанных к аккаунту профилей
            dict(profiles=[profile_item(profile_id=1), profile_item(profile_id=2)]),
            task_data,  # получение данных по task_id
            dict(profiles=[profile_item(uid=TEST_PDD_UID), profile_item(uid=TEST_DEFAULT_UID)]),  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_entered_profiles=[profile_item(uid=TEST_PDD_UID), profile_item(uid=TEST_DEFAULT_UID)],
                social_accounts_account_profiles=[profile_item(profile_id=1), profile_item(profile_id=2)],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_factor_entered_profiles_count=2,
                social_accounts_factor_account_profiles_count=2,
                social_accounts_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_factor_entered_profiles_count=2,
                    social_accounts_factor_account_profiles_count=2,
                    social_accounts_factor_matches_count=1,
                ),
                view.statbox,
            )
            self.assert_social_api_called()

    def test_social_api_fails(self):
        """Социальное API отвечает ошибками на все вызовы"""
        userinfo_response = self.default_userinfo_response()
        self.env.social_api.set_social_api_response_side_effect(BaseSocialApiError)
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_api_status=False,
                ),
                view.statbox,
            )
            self.assert_social_api_called(task_ids=[], user_ids=[])

    def test_social_api_profiles_call_fails(self):
        """Социальное API отвечает ошибками на часть вызовов"""
        userinfo_response = self.default_userinfo_response()
        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        self.env.social_api.set_social_api_response_side_effect([
            # вызов profiles для поиска привязанных к аккаунту профилей
            dict(profiles=[]),
            task_data,  # получение данных по task_id
            BaseSocialApiError,  # получение профиля
        ])
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('social_accounts')

            expected_factors = social_factors(
                social_accounts_entered_accounts=[task_data['profile']],
                social_accounts_factor_entered_accounts_count=1,
                social_accounts_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                social_statbox_entry(
                    social_accounts_factor_entered_accounts_count=1,
                    social_accounts_api_status=False,
                ),
                view.statbox,
            )
            self.assert_social_api_called()
