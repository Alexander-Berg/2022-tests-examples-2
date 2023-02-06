# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)
from functools import partial
from itertools import (
    chain,
    repeat,
)
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_deletion_operations_response,
    blackbox_family_info_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.builders.social_api import (
    BaseSocialApiError,
    SocialApi,
    SocialApiTemporaryError,
)
from passport.backend.core.builders.social_api.faker.social_api import FakeSocialApi
from passport.backend.core.db.schemas import (
    family_info_table as fit,
    family_members_table as fmt,
    phone_bindings_history_delete_tasks_table,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.dbmanager.manager import safe_execute_queries
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE,
    ATTRIBUTE_NAME_TO_TYPE as AN2T,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
)
from passport.backend.core.env import Environment
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
)
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_being_bound,
    build_phone_secured,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.serializers.eav.query import (
    AccountDeletionOperationDeleteQuery,
    EavDeleteAliasQuery,
    EavDeleteAllAttributesQuery,
    EavDeleteAllExtendedAttributesQuery,
    EavDeleteAttributeQuery,
    EavDeleteFromPasswordHistoryQuery,
    EavDeleteSuidQuery,
    InsertLoginIntoReservedQuery,
    MassInsertAliasesIntoRemovedAliasesQuery,
    PassManDeleteAllRecoveryKeysQuery,
)
from passport.backend.core.serializers.query import GenericDeleteQuery
from passport.backend.core.services import Service
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.gender import Gender
from passport.backend.core.useragent.sync import RequestError
from passport.backend.core.ydb.declarative import delete
from passport.backend.core.ydb.schemas import family_invites_table
from passport.backend.dbscripts.account_deleter import cli
from passport.backend.dbscripts.account_deleter.base import delete_account
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_BIRTHDATE1,
    TEST_CITY1,
    TEST_COUNTRY_CODE1,
    TEST_DATETIME1,
    TEST_DEFAULT_AVATAR_KEY1,
    TEST_DISPLAY_NAME1,
    TEST_EMAIL1,
    TEST_EMAIL_ID1,
    TEST_FAMILY_ID,
    TEST_FIRSTNAME1,
    TEST_KIDDISH_LOGIN1,
    TEST_LASTNAME1,
    TEST_LOGIN1,
    TEST_LOGIN2,
    TEST_OPERATION_ID1,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_TIMEZONE1,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
)
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_unixtime
from sqlalchemy import and_


_PERSONAL_ATTRIBUTES_TO_DELETE = [
    AN2T['person.city'],
    AN2T['person.firstname'],
    AN2T['person.lastname'],
    AN2T['account.display_name'],
    AN2T['avatar.default'],
    AN2T['person.birthday'],
    AN2T['person.country'],
    AN2T['person.timezone'],
    AN2T['person.gender'],
]

TEST_DISPLAY_NAME1_SERIALIZED = 'p:%s' % TEST_DISPLAY_NAME1['name']
TEST_KIDDISH_UID1 = TEST_UID3


@with_settings_hosts(
    PERSONAL_DATA_MUST_BE_DELETED_PERIOD=timedelta(days=365),
    ACCOUNT_DELETION_QUARANTINE_PERIOD=timedelta(days=30),
    LOGIN_QUARANTINE_PERIOD=timedelta(days=180).total_seconds(),
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=4,
    SOCIAL_API_URL='http://social/api/'
)
class TestDeleteAccount(TestCase):
    def setUp(self):
        super(TestDeleteAccount, self).setUp()
        self._tvm_credentials_manager = FakeTvmCredentialsManager()
        self._tvm_credentials_manager.start()

        self._tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    '2': {
                        'alias': 'husky',
                        'ticket': TEST_TICKET,
                    },
                    '3': {
                        'alias': 'social_api',
                        'ticket': TEST_TICKET,
                    },
                },
           ),
        )

        self._env = Environment()
        self._social_api_faker = FakeSocialApi()
        self._social_api_faker.start()
        self._social_api = SocialApi()
        self._social_api_faker.set_response_side_effect(
            'delete_all_profiles_by_uid',
            [''],
        )
        self._now = datetime.now().replace(microsecond=0)
        self._datetime_faker = mock.patch(
            'passport.backend.dbscripts.account_deleter.base.datetime',
            now=mock.Mock(return_value=self._now),
        )
        self._datetime_faker.start()

    def tearDown(self):
        self._datetime_faker.stop()
        del self._social_api
        self._social_api_faker.stop()
        del self._social_api_faker
        del self._env
        self._tvm_credentials_manager.stop()
        del self._tvm_credentials_manager
        super(TestDeleteAccount, self).tearDown()

    def _setup_statbox_templates(self):
        self._statbox_faker.bind_entry('subscriptions', _exclude=['ip'], consumer='-')
        self._statbox_faker.bind_entry(
            'account_attr_deleted',
            _inherit_from=['account_modification'],
            _exclude=['ip'],
            operation='deleted',
            new='-',
            consumer='-',
        )
        self._statbox_faker.bind_entry(
            'account_alias_deleted',
            _inherit_from=['account_modification'],
            _exclude=['ip', 'new'],
            entity='aliases',
            operation='removed',
            consumer='-',
        )
        self._statbox_faker.bind_entry(
            'account_karma_deleted',
            _inherit_from=['frodo_karma'],
            _exclude=['ip'],
            action='delete_account',
            login=TEST_LOGIN1,
            old='0',
            new='-',
            registration_datetime='-',
            consumer='-',
            user_agent='-',
        )
        self._statbox_faker.bind_entry(
            'account_deleted',
            mode='account_delete',
            step='account_deleter',
            action='deleted',
            uid=str(TEST_UID1),
        )

        attrs = {
            'account.disabled_status': 'enabled',
            'account.global_logout_datetime': partial(datetime.fromtimestamp(1).strftime, '%Y-%m-%d %H:%M:%S'),
            'account.revoker.app_passwords': partial(datetime.fromtimestamp(1).strftime, '%Y-%m-%d %H:%M:%S'),
            'account.revoker.tokens': partial(datetime.fromtimestamp(1).strftime, '%Y-%m-%d %H:%M:%S'),
            'account.revoker.web_sessions': partial(datetime.fromtimestamp(1).strftime, '%Y-%m-%d %H:%M:%S'),
            'person.country': 'ru',
            'person.language': 'ru',
        }
        for name in attrs:
            self._statbox_faker.bind_entry(
                'kiddish_%s' % name,
                _inherit_from='account_attr_deleted',
                entity=name,
                old=attrs[name],
                uid=str(TEST_KIDDISH_UID1),
            )

        self._statbox_faker.bind_entry(
            'kiddish_alias_deleted',
            _inherit_from=['account_alias_deleted'],
            type=str(EavSerializer.alias_name_to_type('kiddish')),
            uid=str(TEST_KIDDISH_UID1),
        )
        self._statbox_faker.bind_entry(
            'kiddish_karma_deleted',
            _inherit_from=['account_karma_deleted'],
            action='kiddish_delete',
            login=TEST_KIDDISH_LOGIN1,
            uid=str(TEST_KIDDISH_UID1),
        )
        self._statbox_faker.bind_entry(
            'kiddish_subscription_passport',
            _inherit_from=['subscriptions'],
            operation='removed',
            sid=str(Service.by_slug('passport').sid),
            uid=str(TEST_KIDDISH_UID1),
        )

        for log_faker in [self._statbox_faker, self._family_log_faker]:
            log_faker.bind_entry(
                'family_info_modification',
                event='family_info_modification',
                operation='deleted',
                consumer='-',
                user_agent='-',
            )
            log_faker.bind_entry(
                'family_admin_deleted',
                _inherit_from=['family_info_modification'],
                entity='admin_uid',
                family_id=TEST_FAMILY_ID,
                new='-',
                old=str(TEST_UID1),
            )
            log_faker.bind_entry(
                'family_member_deleted',
                _inherit_from=['family_info_modification'],
                attribute='-',
                entity='members',
                entity_id='-',
                family_id=TEST_FAMILY_ID,
                new='-',
                old='-',
            )
            for uid in [TEST_UID1, TEST_UID2]:
                log_faker.bind_entry(
                    'family_member_deleted.%s' % uid,
                    _inherit_from='family_member_deleted',
                    attribute='members.%s.uid' % uid,
                    entity_id=str(uid),
                    old=str(uid),
                )
            log_faker.bind_entry(
                'family_kid_deleted',
                _inherit_from=['family_info_modification'],
                attribute='uid',
                entity='kid',
                entity_id=str(TEST_KIDDISH_UID1),
                family_id=TEST_FAMILY_ID,
                new='-',
                old=str(TEST_KIDDISH_UID1),
            )

    def _build_account(self, **kwargs):
        defaults = dict(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            aliases={'portal': TEST_LOGIN1},
            attributes={
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                'account.deletion_operation_started_at': time() - timedelta(days=400).total_seconds(),
            },
            firstname=None,
            lastname=None,
            language=None,
            country=None,
            city=None,
            gender=None,
            birthdate=None,
        )
        kwargs = deep_merge(defaults, kwargs)
        return build_account(**kwargs)

    def _build_account_personal_data(self):
        return dict(
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            birthdate=TEST_BIRTHDATE1,
            country=TEST_COUNTRY_CODE1,
            gender=Gender.Male,
            display_name=TEST_DISPLAY_NAME1,
            default_avatar_key=TEST_DEFAULT_AVATAR_KEY1,
            city=TEST_CITY1,
            timezone=TEST_TIMEZONE1,
            language='ru',
        )

    def _build_account_emails(self):
        return dict(
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_EMAIL1,
                        EMAIL_NAME_MAPPING['confirmed']: datetime_to_unixtime(TEST_DATETIME1),
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
            ],
        )

    def _build_account_phones(self):
        return deep_merge(
            build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164, is_default=True, is_alias=True),
            build_phone_being_bound(TEST_PHONE_ID2, TEST_PHONE_NUMBER2.e164, TEST_OPERATION_ID1),
        )

    def _create_family(
        self,
        family_id=TEST_FAMILY_ID,
        admin_uid=TEST_UID1,
        uids=None,
        with_kid=None,
    ):
        uids = uids or [TEST_UID1, TEST_UID2]
        kid_uids = [TEST_KIDDISH_UID1] if with_kid else None

        family_info_response = blackbox_family_info_response(
            admin_uid=admin_uid,
            family_id=family_id,
            kid_uids=kid_uids,
            uids=uids,
            with_members_info=True,
        )
        self._blackbox_faker.set_response_value('family_info', family_info_response)
        self._db_faker.serialize(family_info_response, 'family_info')

    def _build_kiddish_account(self):
        return build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            aliases=dict(kiddish=TEST_KIDDISH_LOGIN1),
            birthdate=None,
            city=None,
            firstname=None,
            gender=None,
            lastname=None,
            login=TEST_KIDDISH_LOGIN1,
            uid=TEST_KIDDISH_UID1,
        )

    def _assert_phone_history_delete_task(self, uid=TEST_UID1):
        self._db_faker.check_table_contents(
            'phone_bindings_history_delete_tasks',
            'passportdbcentral',
            [
                {
                    'task_id': 1,
                    'uid': uid,
                    'deletion_started_at': self._now,
                },
            ],
        )

    def _assert_ok_delete_account_event_log(
        self,
        base_deleted=False,
        complete_deleted=False,
        extra_events=None,
        family_admin=False,
        family_member=False,
        family_admin_with_kid=False,
        family_admin_with_member=False,
        with_email=False,
        with_not_blocking_sids=False,
        with_phone=False,
    ):
        """
        Входные параметры
            base_deleted
                Признак, что минимальный набор атрибутов удалён с аккаунта

            complete_deleted
                Признак, что аккаунт удалён полностью

            family_admin
                Принзак, что удаляется админ семьи

            family_member
                Признак, что удаляется участник семьи

            family_admin_with_kid
                Признак, что в удаляемой семье есть ребёнкиш

            family_admin_with_member
                Признак, что в удаляемой семье есть другие участники

            with_email
                Признак, что на удаляемом аккаунте есть e-mail

            with_not_blocking_sids
                Признак, что на удаляемом аккаунте есть неблокирующие сиды

            with_phone
                Признак, что на удаляемом аккаунте есть телефон
        """
        expected = extra_events or dict()

        e = EventCompositor(uid=str(TEST_UID1))

        def opt(name):
            if expected.get(name):
                e(name, expected.get(name))

        if with_not_blocking_sids:
            e('info.mail_status', '-')
            e('sid.rm.info', '1|plato|1')
            e('mail.rm', '1')
            e('sid.rm', '2|plato')
            e('action', 'delete_account')

        if family_admin_with_kid:
            with e.context(uid=str(TEST_KIDDISH_UID1)):
                e('info.login', TEST_KIDDISH_LOGIN1)

                e('info.ena', '-')
                e('info.disabled_status', '-')
                e('info.glogout', '-')
                e('info.tokens_revoked', '-')
                e('info.web_sessions_revoked', '-')
                e('info.app_passwords_revoked', '-')

                e('info.country', '-')
                e('info.tz', '-')
                e('info.lang', '-')

                e('info.password', '-')
                e('info.password_quality', '-')
                e('info.password_update_time', '-')
                e('info.totp', 'disabled')
                e('info.totp_update_time', '-')
                e('info.rfc_totp', 'disabled')

                e('info.karma_prefix', '-')
                e('info.karma_full', '-')
                e('info.karma', '-')
                e('sid.rm', '8|' + TEST_KIDDISH_LOGIN1)
                e('action', 'kiddish_delete')

        if family_admin:
            with e.context(prefix='family.%s.' % TEST_FAMILY_ID):
                e('family_admin', '-')
                e('family_member', '-')
        elif family_member:
            with e.context(prefix='family.%s.' % TEST_FAMILY_ID):
                e('family_member', '-')

        if family_admin_with_member:
            with e.context(
                prefix='family.%s.' % TEST_FAMILY_ID,
                uid=str(TEST_UID2),
            ):
                e('family_member', '-')

        if family_admin_with_kid:
            with e.context(
                prefix='family.%s.' % TEST_FAMILY_ID,
                uid=str(TEST_KIDDISH_UID1),
            ):
                e('family_kid', '-')

        if family_admin:
            e('action', 'delete_family_admin_account')
        elif family_member:
            e('action', 'delete_family_member_account')

        if family_admin_with_member:
            with e.context(uid=str(TEST_UID2)):
                e('action', 'delete_family_admin_account')

        if family_admin_with_kid:
            with e.context(uid=str(TEST_KIDDISH_UID1)):
                e('action', 'delete_family_admin_account')

        if complete_deleted:
            e('info.login', TEST_LOGIN1)
            e('info.ena', '-')
            e('info.disabled_status', '-')

        opt('info.firstname')
        opt('info.lastname')
        opt('info.display_name')
        opt('info.sex')
        opt('info.birthday')
        opt('info.city')
        opt('info.country')

        if base_deleted:
            e('info.tz', '-')

        opt('info.lang')
        opt('info.default_avatar')

        if complete_deleted:
            e('info.password', '-')
            e('info.password_quality', '-')
            e('info.password_update_time', '-')
            e('info.totp', 'disabled')
            e('info.totp_update_time', '-')
            e('info.rfc_totp', 'disabled')
            e('info.karma_prefix', '-')
            e('info.karma_full', '-')
            e('info.karma', '-')

        if with_phone:
            e('alias.phonenumber.rm', TEST_PHONE_NUMBER1.international)
            e('info.phonenumber_alias_search_enabled', '-')

        if complete_deleted:
            e('sid.rm', '8|' + TEST_LOGIN1)

        if with_email:
            e('email.%s' % TEST_EMAIL_ID1, 'deleted')
            e('email.%s.address' % TEST_EMAIL_ID1, TEST_EMAIL1)
            e('email.%s.confirmed_at' % TEST_EMAIL_ID1, '0')
            e('email.%s.is_unsafe' % TEST_EMAIL_ID1, '-')
        elif with_phone:
            with e.context(prefix='phone.1.'):
                e('action', 'deleted')
                e('number', TEST_PHONE_NUMBER1.e164)
            with e.context(prefix='phone.3.'):
                e('action', 'deleted')
                e('number', TEST_PHONE_NUMBER2.e164)
                with e.context(prefix='operation.1.'):
                    e('action', 'deleted')
                    e('security_identity', TEST_PHONE_NUMBER2.digital)
                    e('type', 'bind')
            e('phones.default', '0')
            e('phones.secure', '0')

        if complete_deleted:
            e('deletion_operation', 'deleted')

        if base_deleted:
            e('action', 'delete_account')

        self._event_logger_faker.assert_events_are_logged(e.to_lines())

    def test_invalid_disabled_status(self):
        account = self._build_account()
        account.disabled_status = ACCOUNT_ENABLED
        with self._db_faker.no_recording():
            safe_execute_queries([
                EavDeleteAttributeQuery(TEST_UID1, [AN2T['account.is_disabled']]),
            ])

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([
            AccountDeletionOperationDeleteQuery(TEST_UID1),
            EavDeleteAttributeQuery(TEST_UID1, [AN2T['account.deletion_operation_started_at']]),
        ])

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({
            'action': 'remove_deletion_operation',
            'deletion_operation': 'deleted',
        })

    def test_no_deletion_operation(self):
        account = self._build_account(attributes={'account.deletion_operation_started_at': None})

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([])

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

    def test_quarantine_not_finished(self):
        account = self._build_account(attributes={'account.deletion_operation_started_at': time()})

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([])

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

    def test_not_blocking_and_blocking_sids(self):
        not_blocking_sids = [Service.by_slug('fotki'), Service.by_slug('cards')]
        blocking_sids = [Service.by_slug('balance'), Service.by_slug('partner')]
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds()},
            subscribed_to=not_blocking_sids + blocking_sids,
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([
            EavDeleteAttributeQuery(TEST_UID1, [AN2T['subscription.fotki'], AN2T['subscription.cards']]),
        ])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('fotki').sid)),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('cards').sid)),
        ])

        self._event_logger_faker.assert_events_are_logged({
            'action': 'delete_account',
            'sid.rm': '5|plato,6|plato',
        })

    def test_mail_subscription(self):
        self._husky_api.set_response_value('delete_user', husky_delete_user_response())
        suid2_sids = [Service.by_slug('mail')]
        # Подписка на блокирующий сид нужна, чтобы удалятор не сносил весь
        # аккаунт, а аккуратно удалил только подписку на почту.
        blocking_sids = [Service.by_slug('balance')]
        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds(),
                'subscription.mail.status': '1',
            },
            subscribed_to=suid2_sids + blocking_sids,
            dbfields={
                'subscription.suid.2': '2017',
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        mail_subscription_attributes = [
            AN2T['subscription.mail.login_rule'],
            AN2T['subscription.mail.status'],
        ]
        mail_aliases = [ALIAS_NAME_TO_TYPE['mail']]
        self._db_faker.assert_executed_queries_equal([
            MassInsertAliasesIntoRemovedAliasesQuery(TEST_UID1, mail_aliases),
            EavDeleteAliasQuery(TEST_UID1, mail_aliases),
            EavDeleteAttributeQuery(TEST_UID1, mail_subscription_attributes),
            EavDeleteSuidQuery(TEST_UID1, Service.by_slug('mail').sid),
        ])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('account_attr_deleted', entity='account.mail_status', old='active'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('mail').sid), suid='2017'),
        ])

        self._event_logger_faker.assert_events_are_logged({
            'action': 'delete_account',
            'info.mail_status': '-',
            'mail.rm': '2017',
            'sid.rm': '2|plato',
            'sid.rm.info': '1|plato|2017',
        })

        ok_(self._husky_api.requests)

    def test_mail_deleted_right_away(self):
        self._husky_api.set_response_value('delete_user', husky_delete_user_response())
        suid2_sids = [Service.by_slug('mail')]
        other_sids = [Service.by_slug('fotki')]
        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
                'subscription.mail.status': '1',
            },
            subscribed_to=suid2_sids + other_sids,
            dbfields={
                'subscription.suid.2': '2017',
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        mail_subscription_attributes = [
            AN2T['subscription.mail.login_rule'],
            AN2T['subscription.mail.status'],
        ]
        mail_aliases = [ALIAS_NAME_TO_TYPE['mail']]
        self._db_faker.assert_executed_queries_equal([
            MassInsertAliasesIntoRemovedAliasesQuery(TEST_UID1, mail_aliases),
            EavDeleteAliasQuery(TEST_UID1, mail_aliases),
            EavDeleteAttributeQuery(TEST_UID1, mail_subscription_attributes),
            EavDeleteSuidQuery(TEST_UID1, Service.by_slug('mail').sid),
        ])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('account_attr_deleted', entity='account.mail_status', old='active'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('mail').sid),
                                      suid='2017'),
        ])

        self._event_logger_faker.assert_events_are_logged({
            'action': 'delete_account',
            'info.mail_status': '-',
            'mail.rm': '2017',
            'sid.rm': '2|plato',
            'sid.rm.info': '1|plato|2017',
        })

        ok_(self._husky_api.requests)

        ok_(not account.has_sid(2))

    def test_mail_status_frozen(self):
        self._husky_api.set_response_value('delete_user', husky_delete_user_response())
        suid2_sids = [Service.by_slug('mail')]
        other_sids = [Service.by_slug('fotki')]
        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
                'subscription.mail.status': '2',
            },
            subscribed_to=suid2_sids + other_sids,
            dbfields={
                'subscription.suid.2': '2017',
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        mail_subscription_attributes = [
            AN2T['subscription.mail.login_rule'],
            AN2T['subscription.mail.status'],
        ]
        mail_aliases = [ALIAS_NAME_TO_TYPE['mail']]
        self._db_faker.assert_executed_queries_equal([
            MassInsertAliasesIntoRemovedAliasesQuery(TEST_UID1, mail_aliases),
            EavDeleteAliasQuery(TEST_UID1, mail_aliases),
            EavDeleteAttributeQuery(TEST_UID1, mail_subscription_attributes),
            EavDeleteSuidQuery(TEST_UID1, Service.by_slug('mail').sid),
        ])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('account_attr_deleted', entity='account.mail_status', old='frozen'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('mail').sid), suid='2017'),
        ])

        self._event_logger_faker.assert_events_are_logged({
            'action': 'delete_account',
            'info.mail_status': '-',
            'mail.rm': '2017',
            'sid.rm': '2|plato',
            'sid.rm.info': '1|plato|2017',
        })

        ok_(self._husky_api.requests)

    def test_no_mail_sid(self):
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time()},
            subscribed_to=[Service.by_slug('fotki')],
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([])
        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged([])
        ok_(not self._husky_api.requests)

    def test_blocking_sids_only__yandex(self):
        self._test_with_blocking_sids([Service.by_slug('balance')])

    def test_blocking_sids_only__many(self):
        self._test_with_blocking_sids([Service.by_slug('balance'), Service.by_slug('partner')])

    def _test_with_blocking_sids(self, blocking_sids):
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds()},
            subscribed_to=blocking_sids,
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([])

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

    def test_should_delete_personal_data_but_contract_with_yandex(self):
        contracts_with_yandex = [Service.by_slug('balance')]
        account = self._build_account(
            **deep_merge(
                dict(
                    attributes={'account.deletion_operation_started_at': time() - timedelta(days=366).total_seconds()},
                    subscribed_to=contracts_with_yandex,
                ),
                self._build_account_personal_data(),
            )
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal([])

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

    def test_no_contracts__basic(self):
        self._husky_api.set_response_value('delete_user', husky_delete_user_response())
        suid2_sids = [Service.by_slug('mail')]
        account = self._build_account(
            **deep_merge(
                dict(
                    attributes={
                        'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds(),
                        'subscription.mail.status': '1',
                    },
                    subscribed_to=suid2_sids,
                ),
                self._build_account_personal_data(),
            )
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(is_deleted)

        eq_(self._db_faker.select('aliases', uid=TEST_UID1, db='passportdbcentral'), [])
        eq_(self._db_faker.select('attributes', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('account_deletion_operations', uid=TEST_UID1, db='passportdbshard1'), [])

        mail_aliases = [ALIAS_NAME_TO_TYPE['mail']]
        mail_subscription_attributes = [
            AN2T['subscription.mail.login_rule'],
            AN2T['subscription.mail.status'],
        ]
        pdd_alias_types = [ALIAS_NAME_TO_TYPE[alias] for alias in ['pdd', 'pddalias']]
        to_removed_aliases = sorted(set(ALIAS_NAME_TO_TYPE.values()) - set(pdd_alias_types))
        self._db_faker.assert_executed_queries_equal([
            MassInsertAliasesIntoRemovedAliasesQuery(TEST_UID1, mail_aliases),
            EavDeleteAliasQuery(TEST_UID1, mail_aliases),
            EavDeleteAttributeQuery(TEST_UID1, mail_subscription_attributes),
            EavDeleteSuidQuery(TEST_UID1, Service.by_slug('mail').sid),
            'BEGIN',
            phone_bindings_history_delete_tasks_table.insert().values({
                'uid': TEST_UID1,
                'deletion_started_at': self._now,
            }),
            'COMMIT',
            InsertLoginIntoReservedQuery(TEST_LOGIN1, DatetimeNow() + timedelta(days=149)),
            MassInsertAliasesIntoRemovedAliasesQuery(TEST_UID1, to_removed_aliases),
            EavDeleteAliasQuery(TEST_UID1, sorted(ALIAS_NAME_TO_TYPE.values())),
            EavDeleteAllAttributesQuery(TEST_UID1),
            EavDeleteAllExtendedAttributesQuery(TEST_UID1),
            EavDeleteFromPasswordHistoryQuery(TEST_UID1),
            PassManDeleteAllRecoveryKeysQuery(TEST_UID1),
            AccountDeletionOperationDeleteQuery(TEST_UID1),
            EavDeleteAttributeQuery(TEST_UID1, [AN2T['account.deletion_operation_started_at']]),
        ])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('account_attr_deleted', entity='account.mail_status', old='active'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('mail').sid), suid='1'),
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='account.disabled_status',
                old='disabled_on_deletion',
            ),
            self._statbox_faker.entry('account_alias_deleted', type=str(ALIAS_NAME_TO_TYPE['portal'])),
            self._statbox_faker.entry('account_attr_deleted', entity='person.firstname', old=TEST_FIRSTNAME1),
            self._statbox_faker.entry('account_attr_deleted', entity='person.lastname', old=TEST_LASTNAME1),
            self._statbox_faker.entry('account_attr_deleted', entity='person.language', old='ru'),
            self._statbox_faker.entry('account_attr_deleted', entity='person.country', old=TEST_COUNTRY_CODE1),
            self._statbox_faker.entry('account_attr_deleted', entity='person.gender', old='m'),
            self._statbox_faker.entry('account_attr_deleted', entity='person.birthday', old=TEST_BIRTHDATE1),
            self._statbox_faker.entry('account_attr_deleted', entity='person.display_name', old=TEST_DISPLAY_NAME1_SERIALIZED),
            self._statbox_faker.entry('account_attr_deleted', entity='person.default_avatar', old=TEST_DEFAULT_AVATAR_KEY1),
            self._statbox_faker.entry('account_attr_deleted', entity='person.fullname', old=u'{} {}'.format(TEST_FIRSTNAME1, TEST_LASTNAME1)),
            self._statbox_faker.entry('account_karma_deleted'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('passport').sid)),
            self._statbox_faker.entry('account_deleted'),
        ])

        self._assert_ok_delete_account_event_log(
            base_deleted=True,
            complete_deleted=True,
            extra_events={
                'info.birthday': '-',
                'info.city': '-',
                'info.country': '-',
                'info.default_avatar': '-',
                'info.display_name': '-',
                'info.firstname': '-',
                'info.lang': '-',
                'info.lastname': '-',
                'info.sex': '-',
            },
            with_not_blocking_sids=True,
        )
        self._assert_phone_history_delete_task()

    def test_no_contracts__phones(self):
        account = self._build_account(
            **deep_merge(
                dict(
                    attributes={'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds()},
                ),
                self._build_account_phones(),
            )
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(is_deleted)

        eq_(self._db_faker.select('attributes', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('extended_attributes', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('phone_bindings', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('phone_operations', uid=TEST_UID1, db='passportdbshard1'), [])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='account.disabled_status',
                old='disabled_on_deletion',
            ),
            self._statbox_faker.entry('account_alias_deleted', type=str(ALIAS_NAME_TO_TYPE['portal'])),
            self._statbox_faker.entry('account_alias_deleted', type=str(ALIAS_NAME_TO_TYPE['phonenumber'])),
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='phones.secure',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
                new_entity_id='-',
            ),
            self._statbox_faker.entry('account_karma_deleted'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('passport').sid)),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('phonenumber-alias').sid)),
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='phonenumber_alias.enable_search',
                old='1',
            ),
            self._statbox_faker.entry('account_deleted'),
        ])

        self._assert_ok_delete_account_event_log(
            base_deleted=True,
            complete_deleted=True,
            with_phone=True,
        )
        self._assert_phone_history_delete_task()

    def test_no_contracts__emails(self):
        account = self._build_account(
            **deep_merge(
                dict(
                    attributes={'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds()},
                ),
                self._build_account_emails(),
            )
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(is_deleted)

        eq_(self._db_faker.select('attributes', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('extended_attributes', uid=TEST_UID1, db='passportdbshard1'), [])
        eq_(self._db_faker.select('email_bindings', uid=TEST_UID1, db='passportdbshard1'), [])

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='account.disabled_status',
                old='disabled_on_deletion',
            ),
            self._statbox_faker.entry('account_alias_deleted', type=str(ALIAS_NAME_TO_TYPE['portal'])),
            self._statbox_faker.entry(
                'account_attr_deleted',
                entity='account.emails',
                old=mask_email_for_statbox(TEST_EMAIL1),
                email_id=str(TEST_EMAIL_ID1),
                is_unsafe='1',
                is_suitable_for_restore='0',
                confirmed_at=str(TEST_DATETIME1),
            ),
            self._statbox_faker.entry('account_karma_deleted'),
            self._statbox_faker.entry('subscriptions', operation='removed', sid=str(Service.by_slug('passport').sid)),
            self._statbox_faker.entry('account_deleted'),
        ])
        self._assert_ok_delete_account_event_log(
            base_deleted=True,
            complete_deleted=True,
            with_email=True,
        )
        self._assert_phone_history_delete_task()

    def test_deleting_social_profiles(self):
        account = self._build_account(uid=TEST_UID2)

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(is_deleted)
        eq_(len(self._social_api_faker.requests), 2)
        self._social_api_faker.requests[1].assert_properties_equal(
            method='DELETE',
            url='http://social/api/user/%s?consumer=passport' % TEST_UID2,
        )
        self._assert_phone_history_delete_task(uid=TEST_UID2)

    def test_deleting_social_profiles__invalid_response(self):
        account = self._build_account(uid=TEST_UID2)
        self._social_api_faker.set_response_side_effect(
            'delete_all_profiles_by_uid',
            ['invalid'],
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        self._db_faker.assert_executed_queries_equal(
            [
                EavDeleteAttributeQuery(
                    TEST_UID2,
                    [
                        AN2T['avatar.default'],
                    ],
                ),
            ],
        )

    def test_deleting_social_profiles__network_fail(self):
        account = self._build_account(uid=TEST_UID2)
        self._social_api_faker.set_response_side_effect(
            'delete_all_profiles_by_uid',
            RequestError(),
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)
        self._db_faker.assert_executed_queries_equal(
            [
                EavDeleteAttributeQuery(
                    TEST_UID2,
                    [
                        AN2T['avatar.default'],
                    ],
                ),
            ],
        )

    def _statbox_delete_family(
        self,
        family_id=TEST_FAMILY_ID,
        admin_uid=TEST_UID1,
        uids=None,
    ):
        uids = uids or [TEST_UID1, TEST_UID2]
        entries = []
        family_entries = []
        if admin_uid is not None:
            entries.append(self._statbox_faker.entry('family_admin_deleted'))
            family_entries.append(self._family_log_faker.entry('family_admin_deleted'))
        for uid in uids:
            entries.append(self._statbox_faker.entry('family_member_deleted.%s' % uid))
            family_entries.append(self._family_log_faker.entry('family_member_deleted.%s' % uid))

        return entries, family_entries

    def _build_ydb_delete_family_invites_query(self):
        return delete(
            family_invites_table,
            family_invites_table.c.family_id == TEST_FAMILY_ID,
            optimizer_index='family_id_index',
        ).compile()

    def test_quarantine_delete_family_admin(self):
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time()},
            family_info={'family_id': TEST_FAMILY_ID, 'admin_uid': TEST_UID1},
        )
        self._create_family()

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        self._db_faker.assert_executed_queries_equal(
            [
                'BEGIN',
                GenericDeleteQuery(
                    fit,
                    None,
                    fit.c.family_id == int(str(TEST_FAMILY_ID).lstrip('f')),
                ),
                GenericDeleteQuery(
                    fmt,
                    None,
                    fmt.c.family_id == int(str(TEST_FAMILY_ID).lstrip('f')),
                ),
                'COMMIT',
            ],
        )
        db = 'passportdbcentral'
        eq_(self._db_faker.select('family_members', db=db), [])
        eq_(self._db_faker.select('family_info', db=db), [])

        statbox_expected, family_statbox_expected = self._statbox_delete_family()
        self._statbox_faker.assert_has_written(statbox_expected)
        self._family_log_faker.assert_has_written(family_statbox_expected)
        self.fake_ydb.assert_queries_executed([self._build_ydb_delete_family_invites_query()])

        self._assert_ok_delete_account_event_log(
            family_admin=True,
            family_admin_with_member=True,
        )

    def test_quarantine_delete_family_member(self):
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time()},
            family_info={'family_id': TEST_FAMILY_ID, 'admin_uid': TEST_UID2},
        )
        self._create_family(with_kid=True)
        self._build_kiddish_account()

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        self._db_faker.assert_executed_queries_equal(
            [
                'BEGIN',
                GenericDeleteQuery(
                    fmt,
                    None,
                    and_(
                        fmt.c.family_id == int(str(TEST_FAMILY_ID).lstrip('f')),
                        fmt.c.uid == TEST_UID1,
                    ),
                ),
                'COMMIT',
            ],
        )
        db = 'passportdbcentral'
        eq_(len(self._db_faker.select('family_members', db=db)), 2)
        eq_(len(self._db_faker.select('family_info', db=db)), 1)

        statbox_expected, family_statbox_expected = self._statbox_delete_family(
            admin_uid=None,
            uids=[TEST_UID1],
        )
        self._statbox_faker.assert_has_written(statbox_expected)
        self._family_log_faker.assert_has_written(family_statbox_expected)
        self.fake_ydb.assert_queries_executed([])

        self._assert_ok_delete_account_event_log(family_member=True)

    def test_no_quarantine_delete_family_admin(self):
        account = self._build_account(
            attributes={'account.deletion_operation_started_at': time() - timedelta(days=31).total_seconds()},
            family_info={'family_id': TEST_FAMILY_ID, 'admin_uid': TEST_UID1},
        )
        self._create_family()

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(is_deleted)
        db = 'passportdbcentral'
        eq_(self._db_faker.select('family_members', db=db), [])
        eq_(self._db_faker.select('family_info', db=db), [])
        _, family_statbox_expected = self._statbox_delete_family()
        self._family_log_faker.assert_has_written(family_statbox_expected)
        self._assert_ok_delete_account_event_log(
            base_deleted=True,
            complete_deleted=True,
            family_admin=True,
            family_admin_with_member=True,
        )
        self._assert_phone_history_delete_task()
        self.fake_ydb.assert_queries_executed([self._build_ydb_delete_family_invites_query()])

    def test_delete_family_admin_with_kid(self):
        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
            },
            family_info={
                'admin_uid': TEST_UID1,
                'family_id': TEST_FAMILY_ID,
            },
        )
        self._create_family(with_kid=True)
        self._build_kiddish_account()

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        db = 'passportdbcentral'
        eq_(self._db_faker.select('family_members', db=db), [])
        eq_(self._db_faker.select('aliases', uid=TEST_KIDDISH_UID1, db=db), list())
        eq_(self._db_faker.select('attributes', uid=TEST_KIDDISH_UID1, db='passportdbshard1'), list())

        self._statbox_faker.assert_has_written(
            [
                self._statbox_faker.entry('kiddish_account.global_logout_datetime'),
                self._statbox_faker.entry('kiddish_account.revoker.tokens'),
                self._statbox_faker.entry('kiddish_account.revoker.web_sessions'),
                self._statbox_faker.entry('kiddish_account.revoker.app_passwords'),
                self._statbox_faker.entry('kiddish_account.disabled_status'),
                self._statbox_faker.entry('kiddish_alias_deleted'),
                self._statbox_faker.entry('kiddish_person.language'),
                self._statbox_faker.entry('kiddish_person.country'),
                self._statbox_faker.entry('kiddish_karma_deleted'),
                self._statbox_faker.entry('kiddish_subscription_passport'),
                self._statbox_faker.entry('family_admin_deleted'),
                self._statbox_faker.entry('family_member_deleted.%s' % TEST_UID1),
                self._statbox_faker.entry('family_member_deleted.%s' % TEST_UID2),
                self._statbox_faker.entry('family_kid_deleted'),
            ],
        )

        self._family_log_faker.assert_has_written(
            [
                self._family_log_faker.entry('family_admin_deleted'),
                self._family_log_faker.entry('family_member_deleted.%s' % TEST_UID1),
                self._family_log_faker.entry('family_member_deleted.%s' % TEST_UID2),
                self._family_log_faker.entry('family_kid_deleted'),
            ],
        )

        self._assert_ok_delete_account_event_log(
            family_admin=True,
            family_admin_with_member=True,
            family_admin_with_kid=True,
        )
        self.fake_ydb.assert_queries_executed([self._build_ydb_delete_family_invites_query()])

    def test_revoke_apple_tokens(self):
        self._social_api_faker.set_response_side_effect('delete_tokens_from_account', [''])

        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

        assert len(self._social_api_faker.requests) == 1
        self._social_api_faker.requests[0].assert_properties_equal(
            method='POST',
            url='http://social/api/token/delete_from_account?consumer=passport',
        )
        self._social_api_faker.requests[0].assert_post_data_equals(dict(
            provider_name='apl',
            revoke='1',
            uid=str(TEST_UID1),
        ))

    def test_revoke_apple_tokens__temporary_error(self):
        self._social_api_faker.set_response_side_effect('delete_tokens_from_account', SocialApiTemporaryError())

        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)

    def test_revoke_apple_tokens__other_error(self):
        self._social_api_faker.set_response_side_effect('delete_tokens_from_account', BaseSocialApiError())

        account = self._build_account(
            attributes={
                'account.deletion_operation_started_at': time(),
            },
        )

        is_deleted = delete_account(account, self._env, self._social_api)

        ok_(not is_deleted)


@with_settings_hosts(
    ACCOUNT_DELETION={
        'step_last': {
            'min_age': timedelta(days=365),
            'max_age': timedelta(days=1100),
            'lock_name': '/passport/account_deletion/step_last',
        },
    },
    PERSONAL_DATA_MUST_BE_DELETED_PERIOD=timedelta(days=365),
    ACCOUNT_DELETION_QUARANTINE_PERIOD=timedelta(days=30),
    LOGIN_QUARANTINE_PERIOD=timedelta(days=180).total_seconds(),
)
class TestClient(TestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        self._tvm_credentials_manager = FakeTvmCredentialsManager()
        self._tvm_credentials_manager.start()

        self._tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    '2': {
                        'alias': 'husky',
                        'ticket': TEST_TICKET,
                    },
                    '3': {
                        'alias': 'social_api',
                        'ticket': TEST_TICKET,
                    },
                },
           ),
        )

        self._social_api_faker = FakeSocialApi()
        self._social_api_faker.start()

    def tearDown(self):
        self._social_api_faker.stop()
        self._tvm_credentials_manager.stop()
        super(TestClient, self).tearDown()

    def _build_account(self, **kwargs):
        defaults = dict(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            aliases={
                'portal': TEST_LOGIN1,
            },
            attributes={
                'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                'account.deletion_operation_started_at': time() - timedelta(days=400).total_seconds(),
            },
            firstname=None,
            lastname=None,
            language=None,
            country=None,
            city=None,
            gender=None,
            birthdate=None,
        )
        kwargs = deep_merge(defaults, kwargs)
        return {'userinfo': kwargs}

    def _setup_multi_accounts(self, accounts):
        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([a['userinfo'] for a in accounts]),
        )
        for account in accounts:
            build_account(db_faker=self._db_faker, **account['userinfo'])
        self._social_api_faker.set_response_side_effect(
            'delete_all_profiles_by_uid',
            ['' for _ in accounts],
        )

    def test_no_deletion_operations(self):
        self._blackbox_faker.set_response_value(
            'deletion_operations',
            blackbox_deletion_operations_response([]),
        )

        cli.run(conf_name='step_last', dynamic=True)

        self._db_faker.assert_executed_queries_equal([])

    def test_getting_uids_from_blackbox(self):
        self._blackbox_faker.set_response_value(
            'deletion_operations',
            blackbox_deletion_operations_response(),
        )
        self._setup_multi_accounts([self._build_account()])

        cli.run(conf_name='step_last', dynamic=True)

        self._db_faker.check_missing('aliases', uid=TEST_UID1, db='passportdbcentral')

    def test_fail_does_not_affect_other_accounts(self):
        self._setup_multi_accounts([
            self._build_account(),
            self._build_account(uid=TEST_UID2, login=TEST_LOGIN2, aliases={'portal': TEST_LOGIN2}),
        ])
        self._db_faker.set_side_effect_for_db('passportdbshard1', chain([DBError()], repeat(mock.DEFAULT)))

        cli.run(conf_name='step_last', uids=[TEST_UID1, TEST_UID2])

        self._db_faker.check('aliases', 'value', TEST_LOGIN1, uid=TEST_UID1, type=ALIAS_NAME_TO_TYPE['portal'], db='passportdbcentral')
        self._db_faker.check_missing('aliases', uid=TEST_UID2, db='passportdbcentral')
