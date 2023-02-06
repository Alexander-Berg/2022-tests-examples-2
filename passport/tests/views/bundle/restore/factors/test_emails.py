# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import (
    confirmed_emails_factors,
    confirmed_emails_statbox_entry,
    email_blackwhite_factors,
    email_blackwhite_statbox_entry,
    email_collectors_factors,
    email_collectors_statbox_entry,
    email_folders_factors,
    email_folders_statbox_entry,
    outbound_emails_factors,
    outbound_emails_statbox_entry,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_response,
)
from passport.backend.core.builders.mail_apis.faker import (
    collie_item,
    collie_response,
    furita_blackwhite_response,
    rpop_list_item,
    rpop_list_response,
    wmi_folders_item,
    wmi_folders_response,
)
from passport.backend.core.services import Service
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .test_base import (
    BaseCalculateFactorsMixinTestCase,
    eq_,
)


@with_settings_hosts()
class ConfirmedEmailsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, emails=None):
        return {
            'emails': emails,
        }

    def test_emails_absence_no_match(self):
        """Пользователь считает, что не вводил имейлы, а они есть в истории"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name='email.confirm', value=u'email_2@ya.ru 12345678', timestamp=1, user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('confirmed_emails')

            expected_factors = confirmed_emails_factors(
                emails_history=[
                    {
                        'value': u'email_2@ya.ru',
                        'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None}],
                    },
                ],
                emails_factor_history_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                confirmed_emails_statbox_entry(
                    emails_factor_history_count=1,
                ),
                view.statbox,
            )

    def test_emails_absence_match(self):
        """Пользователь считает, что не вводил имейлы, и это так"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[]),
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('confirmed_emails')

            eq_(factors, confirmed_emails_factors())
            self.assert_entry_in_statbox(
                confirmed_emails_statbox_entry(),
                view.statbox,
            )

    def test_emails_match(self):
        """Указанные email'ы совпали с теми, что есть в истории"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name='email.confirm', value=u'email_2@ya.ru 12345678', timestamp=1, user_ip=TEST_IP),
                event_item(name='email.confirm', value=u'email_3@ya.ru 12345678', timestamp=2, user_ip=TEST_IP),
                event_item(name='email.rpop', value=u'ва@силий@xn--80atjc.xn--p1ai added', timestamp=3, user_ip=TEST_IP),
                event_item(name='email.confirm', value=u'ва@силий@xn--80atjc.xn--p1ai 12345678', timestamp=3, user_ip=TEST_IP),
                event_item(name='email.rpop', value=u'email_5@.рф added', timestamp=4, user_ip=TEST_IP),
                event_item(name='email.delete', value=u'email_3@ya.ru', timestamp=5, user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(emails=[
            u'email_2@ya.ru',
            u'email_3@ya.ru',
            u'ва@силий@окна.рф',
            u'email_5@.рф',
        ])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('confirmed_emails')

            expected_factors = confirmed_emails_factors(
                emails_entered=[
                    u'email_2@ya.ru',
                    u'email_3@ya.ru',
                    u'ва@силий@xn--80atjc.xn--p1ai',
                    u'email_5@.рф',
                ],
                emails_history=[
                    {
                        'value': u'email_2@ya.ru',
                        'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP), 'end': None}],
                    },
                    {
                        'value': u'email_3@ya.ru',
                        'intervals': [{
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=5),
                        }],
                    },
                    {
                        'value': u'ва@силий@xn--80atjc.xn--p1ai',
                        'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3), 'end': None}],
                    },
                    {
                        'value': u'email_5@.рф',
                        'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4), 'end': None}],
                    },
                ],
                emails_matches=[
                    u'email_3@ya.ru',
                    u'email_2@ya.ru',
                    u'ва@силий@xn--80atjc.xn--p1ai',
                    u'email_5@.рф',
                ],
                emails_match_indices=[(0, 1), (1, 0), (2, 2), (3, 3)],
                emails_factor_entered_count=4,
                emails_factor_history_count=4,
                emails_factor_matches_count=4,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                confirmed_emails_statbox_entry(
                    emails_factor_entered_count=4,
                    emails_factor_history_count=4,
                    emails_factor_matches_count=4,
                ),
                view.statbox,
            )

    def test_emails_loose_match(self):
        """Имейл совпал с учетом опечаток"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name='email.confirm', value=u'email_1@ya.ru 1234567', timestamp=1, user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(emails=[u'email_1@ya.com', u'ва@силий@окна.рф'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('confirmed_emails')

            expected_factors = confirmed_emails_factors(
                emails_entered=[
                    u'email_1@ya.com',
                    u'ва@силий@xn--80atjc.xn--p1ai',
                ],
                emails_history=[{
                    'value': u'email_1@ya.ru',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None}],
                }],
                emails_matches=[u'email_1@ya.ru'],
                emails_match_indices=[(0, 0)],
                emails_factor_entered_count=2,
                emails_factor_history_count=1,
                emails_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                confirmed_emails_statbox_entry(
                    emails_factor_entered_count=2,
                    emails_factor_history_count=1,
                    emails_factor_matches_count=1,
                ),
                view.statbox,
            )

    def test_emails_similar_ignored(self):
        """Несколько похожих имейлов не матчим с одним и тем же"""
        userinfo_response = self.default_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name='email.rpop', value=u'email_1@ya.ru added', timestamp=1, user_ip=TEST_IP),
            ]),
        )
        form_values = self.form_values(emails=[u'email_1@ya.com', u'email_1@ya.co'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('confirmed_emails')

            expected_factors = confirmed_emails_factors(
                emails_entered=[
                    u'email_1@ya.com',
                    u'email_1@ya.co'
                ],
                emails_history=[{
                    'value': u'email_1@ya.ru',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP), 'end': None}],
                }],
                emails_matches=[u'email_1@ya.ru'],
                emails_match_indices=[(0, 0)],
                emails_factor_entered_count=2,
                emails_factor_history_count=1,
                emails_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                confirmed_emails_statbox_entry(
                    emails_factor_entered_count=2,
                    emails_factor_history_count=1,
                    emails_factor_matches_count=1,
                ),
                view.statbox,
            )


@with_settings_hosts()
class EmailFoldersHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, email_folders=None):
        return {
            'email_folders': email_folders,
        }

    def test_email_folders_mail_api_not_authorized(self):
        """API почты вернуло 401"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.wmi.set_response_value(
            'folders',
            wmi_folders_response({}),
            status=401,
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_folders')

            expected_factors = email_folders_factors(
                email_folders_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_folders_statbox_entry(
                    email_folders_api_status=False,
                ),
                view.statbox,
            )

    def test_email_folders_match(self):
        """Совпадение почтовых папок, в т.ч. неточное совпадение"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.wmi.set_response_value(
            'folders',
            wmi_folders_response(folders=merge_dicts(
                wmi_folders_item(folder_id=1, name=u'Папка1', is_user=True),
                wmi_folders_item(folder_id=2, name=u'Папка2', is_user=False),  # Системные папки не учитываются
                wmi_folders_item(folder_id=3, name=u'Папка3', is_user=True),
                wmi_folders_item(folder_id=5, name=u'Еще папка?', is_user=True),
            )),
        )
        entered_folders = [u'Papka1', u'Папка2', u'Другая папка']
        form_values = self.form_values(entered_folders)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_folders')

            expected_factors = email_folders_factors(
                email_folders_entered=entered_folders,
                email_folders_actual=[u'Папка1', u'Папка3', u'Еще папка?'],
                email_folders_matches=[u'Папка1', u'Папка3'],
                email_folders_factor_entered_count=3,
                email_folders_factor_actual_count=3,
                email_folders_factor_matches_count=2,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_folders_statbox_entry(
                    email_folders_factor_entered_count=3,
                    email_folders_factor_actual_count=3,
                    email_folders_factor_matches_count=2,
                ),
                view.statbox,
            )

    def test_email_folders_similar_ignored(self):
        """Несколько похожих папок не матчатся с одной и той же"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.wmi.set_response_value(
            'folders',
            wmi_folders_response(folders=wmi_folders_item(folder_id=1, name=u'Папка', is_user=True)),
        )
        entered_folders = [u'Папка1', u'Папка2', u'Papka']
        form_values = self.form_values(entered_folders)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_folders')

            expected_factors = email_folders_factors(
                email_folders_entered=entered_folders,
                email_folders_actual=[u'Папка'],
                email_folders_matches=[u'Папка'],
                email_folders_factor_entered_count=3,
                email_folders_factor_actual_count=1,
                email_folders_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_folders_statbox_entry(
                    email_folders_factor_entered_count=3,
                    email_folders_factor_actual_count=1,
                    email_folders_factor_matches_count=1,
                ),
                view.statbox,
            )

    def test_email_folders_duplicates_ignored(self):
        """Одинаковые папки из ответа API не учитываются"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.wmi.set_response_value(
            'folders',
            wmi_folders_response(folders=merge_dicts(
                wmi_folders_item(folder_id=1, name=u'Папка1', is_user=True),
                wmi_folders_item(folder_id=3, name=u'Папка1', is_user=True),
            )),
        )
        entered_folders = [u'Papka1', u'Папка2', u'Другая папка']
        form_values = self.form_values(entered_folders)
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_folders')

            expected_factors = email_folders_factors(
                email_folders_entered=entered_folders,
                email_folders_actual=[u'Папка1'],
                email_folders_matches=[u'Папка1'],
                email_folders_factor_entered_count=3,
                email_folders_factor_actual_count=1,
                email_folders_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_folders_statbox_entry(
                    email_folders_factor_entered_count=3,
                    email_folders_factor_actual_count=1,
                    email_folders_factor_matches_count=1,
                ),
                view.statbox,
            )


@with_settings_hosts()
class EmailBlackWhiteHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, email_blacklist=None, email_whitelist=None):
        return {
            'email_blacklist': email_blacklist,
            'email_whitelist': email_whitelist,
        }

    def test_email_blackwhite_mail_api_not_authorized(self):
        """API почты вернуло 401"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.furita.set_response_value(
            'blackwhite',
            furita_blackwhite_response({}),
            status=401,
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_blackwhite')

            expected_factors = email_blackwhite_factors(
                email_blacklist_api_status=False,
                email_whitelist_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_blackwhite_statbox_entry(
                    email_blacklist_api_status=False,
                    email_whitelist_api_status=False,
                ),
                view.statbox,
            )

    def test_email_blackwhite_match(self):
        """Частичное совпадение ЧБ списков"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.furita.set_response_value(
            'blackwhite',
            furita_blackwhite_response(
                [u'vasia@почта.рф', u'вася@почта.рф'],
                [u'mail1@mail.ru', u'mail2@mail.ru'],
            ),
        )
        form_values = self.form_values(
            email_blacklist=[u'вася@почта.рф'],
            email_whitelist=[u'mail1@mail.com', u'mail1@mail.ru'],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_blackwhite')

            expected_factors = email_blackwhite_factors(
                email_blacklist_actual=['vasia@xn--80a1acny.xn--p1ai', u'вася@xn--80a1acny.xn--p1ai'],
                email_blacklist_entered=[u'вася@почта.рф'],
                email_blacklist_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
                email_blacklist_factor_actual_count=2,
                email_blacklist_factor_entered_count=1,
                email_blacklist_factor_matches_count=1,
                email_whitelist_actual=['mail1@mail.ru', 'mail2@mail.ru'],
                email_whitelist_entered=['mail1@mail.com', 'mail1@mail.ru'],
                email_whitelist_matches=['mail1@mail.ru', 'mail2@mail.ru'],
                email_whitelist_factor_actual_count=2,
                email_whitelist_factor_entered_count=2,
                email_whitelist_factor_matches_count=2,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_blackwhite_statbox_entry(
                    email_blacklist_factor_actual_count=2,
                    email_blacklist_factor_entered_count=1,
                    email_blacklist_factor_matches_count=1,
                    email_whitelist_factor_actual_count=2,
                    email_whitelist_factor_entered_count=2,
                    email_whitelist_factor_matches_count=2,
                ),
                view.statbox,
            )

    def test_email_blackwhite_duplicates_ignored(self):
        """Одинаковые адреса в запросе / в ответе API не учитываются"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.furita.set_response_value(
            'blackwhite',
            furita_blackwhite_response(
                [u'vasia@почта.рф', u'vasia@xn--80a1acny.xn--p1ai'],
                [u'mail1@mail.ru', u'mail2@mail.ru'],
            ),
        )
        form_values = self.form_values(
            email_blacklist=[u'vasia@почта.рф', u'vasiaa@почта.рф', u'vasia@xn--80a1acny.xn--p1ai'],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_blackwhite')

            expected_factors = email_blackwhite_factors(
                email_blacklist_actual=[u'vasia@xn--80a1acny.xn--p1ai'],
                email_blacklist_entered=[u'vasia@почта.рф', u'vasiaa@почта.рф', u'vasia@xn--80a1acny.xn--p1ai'],
                email_blacklist_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
                email_blacklist_factor_actual_count=1,
                email_blacklist_factor_entered_count=3,
                email_blacklist_factor_matches_count=1,
                email_whitelist_actual=[u'mail1@mail.ru', u'mail2@mail.ru'],
                email_whitelist_factor_actual_count=2,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_blackwhite_statbox_entry(
                    email_blacklist_factor_actual_count=1,
                    email_blacklist_factor_entered_count=3,
                    email_blacklist_factor_matches_count=1,
                    email_whitelist_factor_actual_count=2,
                ),
                view.statbox,
            )


@with_settings_hosts()
class EmailCollectorsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, email_collectors=None):
        return {
            'email_collectors': email_collectors,
        }

    def test_email_collectors_mail_api_not_authorized(self):
        """API почты вернуло 401"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.rpop.set_response_value(
            'list',
            rpop_list_response({}),
            status=401,
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_collectors')

            expected_factors = email_collectors_factors(
                email_collectors_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_collectors_statbox_entry(
                    email_collectors_api_status=False,
                ),
                view.statbox,
            )

    def test_email_collectors_match(self):
        """Частичное совпадение сборщиков"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.rpop.set_response_value(
            'list',
            rpop_list_response(
                [rpop_list_item(u'mail1@mail.com'), rpop_list_item(u'mail2@mail.ru')],
            ),
        )
        form_values = self.form_values(email_collectors=['mail2@mail.com'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_collectors')

            expected_factors = email_collectors_factors(
                email_collectors_entered=['mail2@mail.com'],
                email_collectors_actual=['mail1@mail.com', 'mail2@mail.ru'],
                email_collectors_matches=['mail1@mail.com'],
                email_collectors_factor_entered_count=1,
                email_collectors_factor_actual_count=2,
                email_collectors_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_collectors_statbox_entry(
                    email_collectors_factor_entered_count=1,
                    email_collectors_factor_actual_count=2,
                    email_collectors_factor_matches_count=1,
                ),
                view.statbox,
            )

    def test_email_collectors_duplicates_ignored(self):
        """Одинаковые адреса в запросе в ответе API не учитываются"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.rpop.set_response_value(
            'list',
            rpop_list_response(
                [
                    rpop_list_item(u'vasia@почта.рф'),
                    rpop_list_item(u'vasia@xn--80a1acny.xn--p1ai'),
                ],
            ),
        )
        form_values = self.form_values(
            email_collectors=[
                u'vasia@почта.рф',
                u'vasiaa@почта.рф',
                u'vasia@xn--80a1acny.xn--p1ai',
            ],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('email_collectors')

            expected_factors = email_collectors_factors(
                email_collectors_actual=[u'vasia@xn--80a1acny.xn--p1ai'],
                email_collectors_entered=[
                    u'vasia@почта.рф',
                    u'vasiaa@почта.рф',
                    u'vasia@xn--80a1acny.xn--p1ai',
                ],
                email_collectors_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
                email_collectors_factor_actual_count=1,
                email_collectors_factor_entered_count=3,
                email_collectors_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                email_collectors_statbox_entry(
                    email_collectors_factor_actual_count=1,
                    email_collectors_factor_entered_count=3,
                    email_collectors_factor_matches_count=1,
                ),
                view.statbox,
            )


@with_settings_hosts()
class OutboundEmailsHandlerTestCase(BaseCalculateFactorsMixinTestCase):
    def form_values(self, outbound_emails=None):
        return {
            'outbound_emails': outbound_emails,
        }

    def test_outbound_emails_mail_api_not_authorized(self):
        """API почты вернуло 401"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.collie.set_response_value(
            'search_contacts',
            collie_response({}),
            status=401,
        )
        form_values = self.form_values()
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('outbound_emails')

            expected_factors = outbound_emails_factors(
                outbound_emails_api_status=False,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                outbound_emails_statbox_entry(
                    outbound_emails_api_status=False,
                ),
                view.statbox,
            )

    def test_outbound_emails_match(self):
        """Частичное совпадение исходящих адресов"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.collie.set_response_value(
            'search_contacts',
            collie_response([
                collie_item(email=u'vasia@почта.рф'),
                collie_item(email=u'вася@почта.рф'),
            ]),
        )
        form_values = self.form_values(outbound_emails=[u'вася@почта.рф'])
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('outbound_emails')

            expected_factors = outbound_emails_factors(
                outbound_emails_entered=[u'вася@почта.рф'],
                outbound_emails_actual=[
                    u'vasia@xn--80a1acny.xn--p1ai',
                    u'вася@xn--80a1acny.xn--p1ai',
                ],
                outbound_emails_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
                outbound_emails_factor_entered_count=1,
                outbound_emails_factor_actual_count=2,
                outbound_emails_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                outbound_emails_statbox_entry(
                    outbound_emails_factor_entered_count=1,
                    outbound_emails_factor_actual_count=2,
                    outbound_emails_factor_matches_count=1,
                ),
                view.statbox,
            )

    def test_outbound_emails_duplicates_ignored(self):
        """Одинаковые адреса в запросе / в ответе API не учитываются"""
        userinfo_response = self.default_userinfo_response(subscribed_to=[Service.by_slug('mail').sid])
        self.env.collie.set_response_value(
            'search_contacts',
            collie_response([
                collie_item(email=u'vasia@почта.рф'),
                collie_item(email=u'vasia@xn--80a1acny.xn--p1ai'),
            ]),
        )
        form_values = self.form_values(
            outbound_emails=[
                u'vasia@почта.рф',
                u'vasiaa@почта.рф',
                u'vasia@xn--80a1acny.xn--p1ai',
            ],
        )
        with self.create_base_bundle_view(userinfo_response, form_values) as view:
            factors = view.calculate_factors('outbound_emails')

            expected_factors = outbound_emails_factors(
                outbound_emails_actual=[u'vasia@xn--80a1acny.xn--p1ai'],
                outbound_emails_entered=[
                    u'vasia@почта.рф',
                    u'vasiaa@почта.рф',
                    u'vasia@xn--80a1acny.xn--p1ai',
                ],
                outbound_emails_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
                outbound_emails_factor_actual_count=1,
                outbound_emails_factor_entered_count=3,
                outbound_emails_factor_matches_count=1,
            )
            eq_(factors, expected_factors)
            self.assert_entry_in_statbox(
                outbound_emails_statbox_entry(
                    outbound_emails_factor_actual_count=1,
                    outbound_emails_factor_entered_count=3,
                    outbound_emails_factor_matches_count=1,
                ),
                view.statbox,
            )
