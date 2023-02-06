# -*- coding: utf-8 -*-

import abc
from collections import namedtuple
from datetime import (
    date,
    datetime,
    timedelta,
)
import itertools
import json
import time

import mock
from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from passport.backend.api.common.authorization import (
    build_cookie_yandex_login,
    build_cookie_yp,
    build_cookie_ys,
)
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.common.processes import (
    PROCESS_ACCOUNT_DELETE_V2,
    PROCESS_WEB_REGISTRATION,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle import test_base_data
from passport.backend.api.tests.views.bundle.mdapi.base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_HOST,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_family_info_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.counters.buckets import get_buckets
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE as ANT,
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_ANT,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.env.env import Environment
from passport.backend.core.mailer.faker.mail_utils import assert_email_message_sent
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_account,
    build_phone_bound,
    build_phone_secured,
    TEST_DATE,
)
from passport.backend.core.services import (
    BLOCKING_SIDS,
    Service,
)
from passport.backend.core.test.consts import (
    TEST_KIDDISH_LOGIN1,
    TEST_REGISTRAION_DATETIME1,
    TEST_SCHOLAR_LOGIN1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tracks.model import AuthTrack
from passport.backend.core.types.account.account import (
    KINOPOISK_UID_BOUNDARY,
    PDD_UID_BOUNDARY,
)
from passport.backend.core.types.display_name import DisplayName
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.login.login import masked_login
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.useragent.sync import RequestError
from passport.backend.utils.common import deep_merge
from passport.backend.utils.string import smart_bytes
from passport.backend.utils.time import (
    datetime_to_integer_unixtime,
    DEFAULT_FORMAT,
)
import six


# FIXME: грязный хак - надо почистить вместе с чисткой всех данных для тестирования

TEST_UID = 1
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_KINOPOISK_UID = KINOPOISK_UID_BOUNDARY + 1
TEST_ANOTHER_UID = TEST_UID + 1
TEST_PHONE_USER_UID = TEST_UID + 2
TEST_SOCIAL_UID = TEST_UID + 3
TEST_KID_UID1 = TEST_UID + 4
TEST_KID_UID2 = TEST_UID + 5

TEST_LOGIN = 'login'
TEST_PHONE_LOGIN = 'login_with_phone'
TEST_SOCIAL_LOGIN = 'uid-test'
TEST_PDD_DOMAIN = 'yandex.ru'
TEST_PDD_LOGIN = '@'.join([TEST_LOGIN, TEST_PDD_DOMAIN])
TEST_ANOTHER_LOGIN = TEST_LOGIN + 'another'
TEST_IP = '3.3.3.3'

TEST_PHONE_ID = 1
TEST_PHONE_NUMBER = PhoneNumber.parse('+79033123456')

TEST_PHONE_CREATION_DATE = datetime(2000, 1, 2, 10, 11, 27)
TEST_PHONE_BOUND_DATE = datetime(2000, 1, 2, 10, 11, 28)
TEST_PHONE_SECURED_DATE = datetime(2000, 1, 2, 10, 11, 29)
TEST_PHONE_CONFIRMED_DATE = datetime(2000, 1, 2, 10, 11, 30)

TEST_ACCOUNT_DELETE_BASE_GRANT = 'account.delete'
TEST_ACCOUNT_DELETE_ANY_GRANT = 'account.delete_any'
TEST_ACCOUNT_DELETE_PDD_GRANT = 'account.delete_pdd'
TEST_ACCOUNT_DELETE_KINOPOISK_GRANT = 'account.delete_kinopoisk'
TEST_ACCOUNT_DELETE_SCHOLAR_GRANT = 'account.delete_scholar'
TEST_ACCOUNT_DELETE_FEDERAL_GRANT = 'account.delete_federal'

TEST_FAMILY_ID = 'f1'
TEST_FAMILY_INFO = {'admin_uid': TEST_UID, 'family_id': TEST_FAMILY_ID}

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_LONG_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_DISPLAY_NAME1 = DisplayName(u'Попосерик2020')


class TEST_TRANSLATIONS(object):
    NOTIFICATIONS = {
        'ru': {
            u'confirmation_code_for_account_deletion_email_subject': u'Письмецо в конверте подожди не рви',
            u'email_sender_display_name': u'Яндекс.Паспорт',
            u'greeting': u'Здравствуйте, %FIRST_NAME%!',

            u'Для подтверждения удаления аккаунта <b>%(MASKED_LOGIN)s</b> на Яндексе, '
            u'введите следующий код подтверждения на странице удаления:': u'Для подтверждения удаления аккаунта '
            u'<b>%(MASKED_LOGIN)s</b> на Яндексе, введите следующий код подтверждения на странице удаления:',

            u'Срок действия кода &mdash; 3 часа с момента отправки сообщения.': u'Срок действия кода &mdash; 3 часа с момента отправки сообщения.',
            u'Если вы не запрашивали код для удаления аккаунта &mdash; это мог сделать злоумышленник.': u'Если вы не запрашивали код для удаления аккаунта &mdash; это мог сделать злоумышленник.',
            u'В таком случае:': u'В таком случае:',
            u'<a href="%(RESTORE_URL)s" target="_blank">восстановите доступ</a> к аккаунту;': u'<a href="%(RESTORE_URL)s" target="_blank">восстановите доступ</a> к аккаунту;',

            u'<a href="%(PROFILE_URL)s" target="_blank">проверьте актуальность</a> '
            u'привязанного номера телефона и почты для восстановления.': u'<a href="%(PROFILE_URL)s" target="_blank">проверьте актуальность</a> '
            u'привязанного номера телефона и почты для восстановления.',

            u'signature.secure': u'С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID',
            u'feedback': u'Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки Яндекса Вы можете через %FEEDBACK_URL_BEGIN%форму обратной связи%FEEDBACK_URL_END%.',
            u'feedback_url': u'https://feedback2.yandex.ru/',
            u'logo_url': u'https://logo.url/',
        },
    }

    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


Response = namedtuple('Response', ['content', 'status_code'])


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env, response_dict):
        self._env = env
        self._kwargs = dict()
        self._response_dict = response_dict

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_userinfo_response(**self.kwargs)
        self._response_dict[self.kwargs.get('uid')] = response
        self._env.db.serialize(response)


class MinimalKiddishBlackboxResponse(IBlackboxResponse):
    def __init__(self, env, response_dict):
        self._userinfo_response = UserinfoBlackboxResponse(env, response_dict)
        self._userinfo_response.kwargs.update(self.build_minimal_kiddish_kwargs())

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()

    @staticmethod
    def build_minimal_kiddish_kwargs():
        return dict(
            aliases=dict(kiddish=TEST_KIDDISH_LOGIN1),
            birthdate=None,
            city=None,
            dbfields={
                'userinfo.reg_date.uid': TEST_REGISTRAION_DATETIME1,
            },
            display_name=TEST_DISPLAY_NAME1.as_dict(),
            family_info=dict(
                admin_uid=TEST_UID,
                family_id=TEST_FAMILY_ID,
            ),
            firstname=None,
            gender=None,
            lastname=None,
            login=TEST_KIDDISH_LOGIN1,
            uid=TEST_KID_UID1,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    LOGIN_QUARANTINE_PERIOD=1,
    SOCIAL_API_URL='https://social/api/',
)
class TestAccountDeleteView(BaseBundleTestViews):

    default_url = '/1/bundle/account/%s/' % TEST_UID
    http_method = 'delete'
    http_query_args = dict(
        consumer='dev',
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )
    mocked_grants = {
        'account': [
            'delete',
            'delete_any',
        ],
    }

    def __init__(self, *args, **kwargs):
        super(TestAccountDeleteView, self).__init__(*args, **kwargs)

        self.alias_name = 'portal'
        self.login = TEST_LOGIN
        self.scholar_password = None

    def blackbox_userinfo_selector(self, *args, **kwargs):
        method, url, params = args

        if isinstance(params['uid'], six.string_types):
            uids = set(map(int, params['uid'].split(',')))
        else:
            uids = set([params['uid']])

        users = list()
        for uid in uids:
            users.append(json.loads(self.userinfo[uid])['users'][0])
        content = json.dumps(dict(users=users)).encode('utf-8')

        return Response(status_code=200, content=content)

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager = self.env.track_manager.get_manager()

        self.env.grants.set_grants_return_value(
            mock_grants(grants=self.mocked_grants),
        )

        self.setup_statbox_templates()

        self.userinfo = {}

        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            self.blackbox_userinfo_selector,
        )
        self.env.social_api.set_response_side_effect('delete_all_profiles_by_uid', [''])

        self.now = datetime.now().replace(microsecond=0)
        self.datetime_faker = mock.patch(
            'passport.backend.api.views.bundle.account.delete.datetime',
            now=mock.Mock(return_value=self.now),
        )
        self.datetime_faker.start()

    def tearDown(self):
        self.datetime_faker.stop()
        self.env.stop()
        del self.env
        del self.track_manager

    def set_request_uid(self, uid):
        self.default_url = '/1/bundle/account/%s/' % uid

    def create_federal_user(
        self,
        uid,
        login=None,
        with_mail_sid=False,
        **kwargs
    ):
        login = login or self.login

        subscribed_to = [8]
        dbfields = {}
        if with_mail_sid:
            subscribed_to.append(2)
            dbfields.update({
                'subscription.suid.2': 1,
            })

        blackbox_kwargs = deep_merge(
            dict(
                aliases={
                    'federal': login,
                    'pdd': login,
                },
                uid=uid,
                login=login,
                subscribed_to=subscribed_to,
                dbfields=dbfields,
            ),
            kwargs,
        )

        blackbox_response = blackbox_userinfo_response(**blackbox_kwargs)
        self.userinfo[uid] = blackbox_response
        self.env.db.serialize(blackbox_response)

    def create_user(
        self,
        uid,
        login=None,
        secure_phone_number=None,
        with_mail_sid=False,
        alias_name=None,
        **kwargs
    ):
        alias_name = alias_name or self.alias_name
        login = login or self.login

        subscribed_to = [8]
        dbfields = {}
        if with_mail_sid:
            subscribed_to.append(2)
            dbfields.update({
                'subscription.suid.2': 1,
            })

        blackbox_kwargs = deep_merge(
            dict(
                aliases={alias_name: login},
                uid=uid,
                login=login,
                subscribed_to=subscribed_to,
                dbfields=dbfields,
            ),
            kwargs,
        )

        if secure_phone_number:
            phone_kwargs = {
                'phone_created': TEST_PHONE_CREATION_DATE,
                'phone_bound': TEST_PHONE_BOUND_DATE,
                'phone_confirmed': TEST_PHONE_CONFIRMED_DATE,
                'phone_secured': TEST_PHONE_SECURED_DATE,
                'is_default': False,
            }
            blackbox_kwargs = deep_merge(
                blackbox_kwargs,
                build_phone_secured(
                    TEST_PHONE_ID,
                    secure_phone_number,
                    **phone_kwargs
                ),
            )

        shard_name = 'passportdbshard%d' % (2 if uid > PDD_UID_BOUNDARY else 1)

        blackbox_response = blackbox_userinfo_response(**blackbox_kwargs)
        self.userinfo[uid] = blackbox_response
        self.env.db.serialize(blackbox_response)

        self.env.db.insert(
            'password_history',
            uid=uid,
            ts=DatetimeNow(),
            encrypted_password='1',
            reason=0,
            db=shard_name,
        )
        self.env.db.insert(
            'extended_attributes',
            uid=uid,
            entity_type=999,
            entity_id=999,
            type=999,
            value='Hello, world!',
            db=shard_name,
        )

    def create_family(
        self,
        family_id=TEST_FAMILY_ID,
        admin_uid=TEST_UID,
        uids=None,
        kid_uids=None,
    ):
        uids = uids or [TEST_UID, TEST_ANOTHER_UID]
        kid_uids = kid_uids or [TEST_KID_UID1, TEST_KID_UID2]

        self.env.db.insert(
            'family_info',
            db='passportdbcentral',
            family_id=str(family_id).lstrip('f'),
            admin_uid=admin_uid,
            meta='',
        )
        for place, uid in itertools.chain(
            enumerate(uids),
            enumerate(kid_uids, start=100),
        ):
            self.env.db.insert(
                'family_members',
                db='passportdbcentral',
                family_id=str(family_id).lstrip('f'),
                uid=uid,
                place=place,
            )
        self.env.db.reset_mocks('passportdbcentral')

        self.env.blackbox.set_response_value(
            'family_info',
            blackbox_family_info_response(
                family_id=family_id,
                admin_uid=admin_uid,
                uids=uids,
                kid_uids=kid_uids,
                with_members_info=True,
            ),
        )

        for kid_uid in kid_uids:
            kiddish_response = MinimalKiddishBlackboxResponse(self.env, self.userinfo)
            kiddish_response.kwargs.update(
                aliases=dict(kiddish=TEST_KIDDISH_LOGIN1 + str(kid_uid)),
                login=TEST_KIDDISH_LOGIN1 + str(kid_uid),
                uid=kid_uid,
            )
            kiddish_response.setup()

    def setup_statbox_templates(self):
        kid_uids = [TEST_KID_UID1, TEST_KID_UID2]
        self.env.statbox.bind_base(
            consumer='dev',
            user_agent='curl',
        )
        for action in ['submitted', 'deleted', 'blocked_on_delete']:
            self.env.statbox.bind_entry(
                action,
                action=action,
                mode='account_delete',
                uid=str(TEST_UID),
                ip=TEST_IP,
            )
        self.env.statbox.bind_entry(
            'account_modification',
            event='account_modification',
            ip=TEST_IP,
            new='-',
            operation='deleted',
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'set_disabled_status',
            event='account_modification',
            entity='account.disabled_status',
            operation='updated',
            old='enabled',
            new='disabled_on_deletion',
            uid=str(TEST_UID),
            ip=TEST_IP,
        )
        for kid_uid in kid_uids:
            self.env.statbox.bind_entry(
                'set_disabled_status_' + str(kid_uid),
                _inherit_from=['set_disabled_status'],
                uid=str(kid_uid),
            )
        self.env.statbox.bind_entry(
            'rm_subscription',
            event='account_modification',
            entity='subscriptions',
            operation='removed',
            uid=str(TEST_UID),
            ip=TEST_IP,
        )
        self.env.statbox.bind_entry(
            'rm_alias',
            event='account_modification',
            entity='aliases',
            operation='removed',
            uid=str(TEST_UID),
            ip=TEST_IP,
        )

        for logger in [self.env.family_logger, self.env.statbox]:
            logger.bind_entry(
                'family_info_modification',
                consumer='dev',
                event='family_info_modification',
                family_id=TEST_FAMILY_ID,
                ip=TEST_IP,
                new='-',
                operation='deleted',
                user_agent='curl',
            )
            logger.bind_entry(
                'family_admin_deleted',
                _inherit_from=['family_info_modification'],
                entity='admin_uid',
                old=str(TEST_UID),
            )
            for member_uid in [TEST_UID, TEST_ANOTHER_UID]:
                logger.bind_entry(
                    'family_member_deleted_' + str(member_uid),
                    _inherit_from=['family_info_modification'],
                    attribute='members.%s.uid' % member_uid,
                    entity='members',
                    entity_id=str(member_uid),
                    old=str(member_uid),
                )
            for kid_uid in kid_uids:
                logger.bind_entry(
                    'family_kid_deleted_' + str(kid_uid),
                    _inherit_from=['family_info_modification'],
                    attribute='uid',
                    entity='kid',
                    entity_id=str(kid_uid),
                    old=str(kid_uid),
                )

    def check_deletion_is_recorded_in_statbox(
        self,
        uid=TEST_UID,
        with_phones=False,
        with_mail_sid=False,
        with_family=False,
        family_admin=False,
        kid_uids=None,
        is_federal=False,
    ):
        is_pdd = uid > PDD_UID_BOUNDARY
        is_kinopoisk = PDD_UID_BOUNDARY > uid > KINOPOISK_UID_BOUNDARY
        entries = [
            self.env.statbox.entry(
                'submitted',
                uid=str(uid),
            ),
        ]

        family_entries = []
        if with_family:
            uids = [TEST_UID]
            kid_uids = kid_uids or list()
            if family_admin:
                for kid_uid in kid_uids:
                    entries.append(self.env.statbox.entry('set_disabled_status_' + str(kid_uid)))
                uids.append(TEST_ANOTHER_UID)
                entries.append(self.env.statbox.entry('family_admin_deleted'))
                family_entries.append(self.env.family_logger.entry('family_admin_deleted'))
            for _uid in uids:
                entries.append(self.env.statbox.entry('family_member_deleted_' + str(_uid)))
                family_entries.append(self.env.family_logger.entry('family_member_deleted_' + str(_uid)))
            for kid_uid in kid_uids:
                entries.append(self.env.statbox.entry('family_kid_deleted_' + str(kid_uid)))
                family_entries.append(self.env.family_logger.entry('family_kid_deleted_' + str(kid_uid)))

        beginning_of_time = datetime.fromtimestamp(1).strftime('%Y-%m-%d %H:%M:%S')

        for entity, value in [
            ('account.global_logout_datetime', beginning_of_time),
            ('account.revoker.tokens', beginning_of_time),
            ('account.revoker.web_sessions', beginning_of_time),
            ('account.revoker.app_passwords', beginning_of_time),
            ('account.disabled_status', 'enabled'),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    old=value,
                    uid=str(uid),
                ),
            )

        entries.append(
            self.env.statbox.entry(
                'rm_alias',
                type=str(ANT[self.alias_name]),
                uid=str(uid),
            ),
        )
        if is_federal:
            entries.append(
                self.env.statbox.entry(
                    'rm_alias',
                    type=str(ANT['federal']),
                    uid=str(uid),
                )
            )

        if with_phones:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    old=TEST_PHONE_NUMBER.masked_format_for_statbox,
                    old_entity_id=str(TEST_PHONE_ID),
                    new_entity_id='-',
                    uid=str(uid),
                ),
            )

        if self.scholar_password:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['new'],
                    entity='account.scholar_password',
                    uid=str(uid),
                ),
            )

        for entity, value in [
            ('person.firstname', '\\\\u0414'),
            ('person.lastname', '\\\\u0424'),
            ('person.language', 'ru'),
            ('person.country', 'ru'),
            ('person.gender', 'm'),
            ('person.birthday', '1963-05-15'),
            ('person.fullname', '\\\\u0414 \\\\u0424'),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    old=value,
                    uid=str(uid),
                ),
            )

        if is_pdd or is_federal:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='domain_name',
                    old=TEST_PDD_DOMAIN,
                    uid=str(uid),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='domain_id',
                    old='1',
                    uid=str(uid),
                ),
            ]

        entries += [
            self.env.statbox.entry(
                'account_modification',
                _exclude=['operation'],
                entity='karma',
                action='account_delete',
                destination='frodo',
                old='0',
                login='-' if is_kinopoisk else self.login,
                registration_datetime='-',
                suid='1' if with_mail_sid else '-',
                uid=str(uid),
            ),
            self.env.statbox.entry(
                'rm_subscription',
                sid='8',
                uid=str(uid),
            ),
        ]
        if with_mail_sid:
            entries.append(
                self.env.statbox.entry(
                    'rm_subscription',
                    sid='2',
                    suid='1',
                    uid=str(uid),
                ),
            )

        entries.append(
            self.env.statbox.entry(
                'deleted',
                uid=str(uid),
            ),
        )

        self.env.statbox.assert_equals(entries)
        self.env.family_logger.assert_equals(family_entries)

    def check_db_entries_processed(
        self,
        uid,
        login=None,
        shard_query_count=4,
        central_query_count=4,
    ):
        login = login or self.login
        is_pdd = uid > PDD_UID_BOUNDARY
        is_kinopoisk = PDD_UID_BOUNDARY > uid > KINOPOISK_UID_BOUNDARY

        shard_db_name = 'passportdbshard%d' % (2 if is_pdd or is_kinopoisk else 1)

        for table, db in (
            ('attributes', shard_db_name),
            ('extended_attributes', shard_db_name),
            ('aliases', 'passportdbcentral'),
            ('password_history', shard_db_name),
            ('passman_recovery_keys', shard_db_name),
        ):
            records_found = self.env.db.select(
                table,
                db=db,
                uid=uid,
            )
            eq_(
                records_found,
                [],
                'Found records for UID=%s in table "%s" (%s), while expecting to find none: %s' % (
                    uid, table, db, records_found,
                ),
            )

        self.env.db.check_table_contents(
            'phone_bindings_history_delete_tasks',
            'passportdbcentral',
            [
                {
                    'task_id': 1,
                    'uid': uid,
                    'deletion_started_at': self.now,
                },
            ],
        )

        if not (is_pdd or is_kinopoisk):
            self.env.db.check(
                'reserved_logins',
                'login',
                smart_bytes(login),
                db='passportdbcentral',
            )

        eq_(
            self.env.db.query_count('passportdbcentral'),
            central_query_count,
        )
        eq_(
            self.env.db.query_count(shard_db_name),
            shard_query_count,
        )

    def check_db_family_deletion(
        self,
        family_id,
        member_uids,
        is_admin=True,
        kid_uids=None,
    ):
        kid_uids = kid_uids or list()

        for uid in member_uids + kid_uids:
            records_found = self.env.db.select(
                'family_members',
                db='passportdbcentral',
                uid=uid,
                family_id=str(family_id).lstrip('f'),
            )
            eq_(
                records_found,
                [],
                'Found family member record for family_id=%s uid=%s' % (family_id, uid),
            )

        records_found = self.env.db.select(
            'family_info',
            db='passportdbcentral',
            family_id=int(str(family_id).lstrip('f')),
        )
        eq_(len(records_found), 1 - is_admin)

        for kid_uid in kid_uids:
            self.env.db.check_db_attr(kid_uid, 'account.is_disabled', str(ACCOUNT_DISABLED_ON_DELETION))
            self.env.db.check_db_attr(kid_uid, 'account.deletion_operation_started_at', TimeNow())

            deletion_operations = self.env.db.select('account_deletion_operations', uid=kid_uid, db='passportdbshard1')
            self.assertEqual(len(deletion_operations), 1)
            self.assertEqual(deletion_operations[0]['started_at'], DatetimeNow())

    def check_another_users_db_entries_are_intact(self, uid, login):
        for table, db in (
            ('attributes', 'passportdbshard1'),
            ('extended_attributes', 'passportdbshard1'),
            ('aliases', 'passportdbcentral'),
            ('password_history', 'passportdbshard1'),
        ):
            records_found = self.env.db.select(
                table,
                db=db,
                uid=uid,
            )
            ok_(
                len(records_found) > 0,
                'No records found for uid=%s in table "%s", but there should be.' % (
                    uid,
                    table,
                ),
            )

        self.env.db.check_missing(
            'reserved_logins',
            login=login,
            db='passportdbcentral',
        )

    def check_deletion_recorded_in_historydb(
        self,
        uid,
        login=None,
        with_phones=False,
        with_mail_sid=False,
        with_family=False,
        family_admin=False,
        kid_uids=None,
    ):
        login = login or self.login
        is_pdd = uid > PDD_UID_BOUNDARY
        is_kinopoisk = PDD_UID_BOUNDARY > uid > KINOPOISK_UID_BOUNDARY

        historydb_record = [
            ('info.login', None if is_kinopoisk else smart_bytes(login)),
            ('action', 'account_delete'),
            ('consumer', 'dev'),
            ('user_agent', 'curl'),
        ]
        if with_mail_sid:
            historydb_record += [
                ('mail.rm', '1'),
                ('sid.rm', '8|%s,2|%s' % (smart_bytes(login), smart_bytes(login))),
                ('sid.rm.info', '%s|%s|1' % (uid, smart_bytes(login)))
            ]
        else:
            historydb_record += [
                ('sid.rm', '8' if is_kinopoisk else '8|%s' % smart_bytes(login)),
            ]

        empty_fields = [
            'info.ena',
            'info.disabled_status',
            'info.glogout',
            'info.tokens_revoked',
            'info.web_sessions_revoked',
            'info.app_passwords_revoked',
            'info.firstname',
            'info.lastname',
            'info.sex',
            'info.birthday',
            'info.city',
            'info.country',
            'info.tz',
            'info.lang',
            'info.password',
            'info.password_quality',
            'info.password_update_time',
            'info.totp',
            'info.totp_update_time',
            'info.rfc_totp',
            'info.karma_prefix',
            'info.karma_full',
            'info.karma',
        ]

        if is_pdd:
            empty_fields.insert(10, 'info.domain_id')
            empty_fields.insert(10, 'info.domain_name')

        if self.scholar_password:
            empty_fields.append('info.scholar_password')

        for field in empty_fields:
            value = 'disabled' if field in ('info.totp', 'info.rfc_totp') else '-'
            historydb_record.append((field, value))

        if with_phones:
            historydb_record.extend([
                ('phone.1.action', 'deleted'),
                ('phone.1.number', TEST_PHONE_NUMBER.e164),
                ('phones.secure', '0'),
            ])

        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record if v is not None
        ]

        if with_family:
            family_account_delete_action = 'family_%s_account_delete' % ('admin' if family_admin else 'member')

            family_member_uids = [TEST_UID, TEST_ANOTHER_UID] if family_admin else [TEST_UID]
            for uid in family_member_uids:
                e = EventCompositor(uid=str(uid))
                e('action', family_account_delete_action)
                e('consumer', 'dev'),
                e('user_agent', TEST_USER_AGENT),
                e('family.f1.family_member', '-')
                historydb_entries.extend(e.to_lines())

            kid_uids = kid_uids or list()
            for kid_uid in kid_uids:
                e = EventCompositor(uid=str(kid_uid))
                e('action', family_account_delete_action)
                e('consumer', 'dev'),
                e('user_agent', TEST_USER_AGENT),
                e('family.f1.family_kid', '-')
                historydb_entries.extend(e.to_lines())

            if family_admin:
                e = EventCompositor(uid=str(TEST_UID))
                e('family.f1.family_admin', '-')
                historydb_entries.extend(e.to_lines())

                for kid_uid in kid_uids:
                    e = EventCompositor(uid=str(kid_uid))
                    e('info.ena', '0')
                    e('info.disabled_status', str(ACCOUNT_DISABLED_ON_DELETION))
                    e('deletion_operation', 'created')
                    e('action', 'start_kiddish_deletion')
                    e('consumer', 'dev')
                    e('user_agent', TEST_USER_AGENT)
                    historydb_entries.extend(e.to_lines())

        self.assert_events_are_logged(self.env.handle_mock, historydb_entries)

    def check_user_is_blocked_on_deletion(self, uid):
        self.env.db.check(
            'attributes',
            'account.is_disabled',
            str(ACCOUNT_DISABLED_ON_DELETION),
            uid=uid,
            db='passportdbshard1',
        )

        historydb_record = [
            ('action', 'account_delete'),
            ('info.ena', '0'),
            ('info.disabled_status', '2'),
            ('consumer', 'dev'),
            ('user_agent', 'curl'),
        ]
        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record if v is not None
        ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            historydb_entries,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', uid=str(uid)),
            self.env.statbox.entry('blocked_on_delete', uid=str(uid)),
            self.env.statbox.entry('set_disabled_status', uid=str(uid)),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def check_social_profiles_deleted(self, uid):
        eq_(len(self.env.social_api.requests), 1)
        self.env.social_api.requests[0].assert_properties_equal(
            method='DELETE',
            url='https://social/api/user/%s?consumer=passport' % uid,
        )

    def check_social_profiles_not_deleted(self, uid):
        eq_(len(self.env.social_api.requests), 0)

    def test_normal_delete_ok(self):
        self.create_user(TEST_UID)
        self.create_user(TEST_ANOTHER_UID, TEST_ANOTHER_LOGIN)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_deletion_is_recorded_in_statbox()
        self.check_db_entries_processed(TEST_UID)
        self.check_another_users_db_entries_are_intact(
            TEST_ANOTHER_UID,
            TEST_ANOTHER_LOGIN,
        )
        self.check_deletion_recorded_in_historydb(TEST_UID)
        self.check_social_profiles_deleted(TEST_UID)

    def test_pdd_delete_ok(self):
        self.alias_name = 'pdd'
        self.login = TEST_PDD_LOGIN
        self.create_user(
            TEST_PDD_UID,
            domid=1,
            domain=TEST_PDD_DOMAIN,
            with_mail_sid=True,
        )
        self.create_user(TEST_ANOTHER_UID, TEST_ANOTHER_LOGIN, alias_name='portal')
        self.set_request_uid(TEST_PDD_UID)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_deletion_is_recorded_in_statbox(uid=TEST_PDD_UID, with_mail_sid=True)
        self.check_db_entries_processed(TEST_PDD_UID, central_query_count=5)
        self.check_another_users_db_entries_are_intact(
            TEST_ANOTHER_UID,
            TEST_ANOTHER_LOGIN,
        )
        self.check_deletion_recorded_in_historydb(TEST_PDD_UID, with_mail_sid=True)
        self.check_social_profiles_deleted(TEST_PDD_UID)
        eq_(len(self.env.husky_api.requests), 1)

    def test_federal_delete_ok(self):
        self.alias_name = 'pdd'
        self.login = TEST_PDD_LOGIN
        self.create_federal_user(
            TEST_UID,
            domid=1,
            domain=TEST_PDD_DOMAIN,
            with_mail_sid=True,
        )
        self.set_request_uid(TEST_UID)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())

        resp = self.make_request()
        self.assert_ok_response(resp)

        self.check_deletion_is_recorded_in_statbox(uid=TEST_UID, with_mail_sid=True, is_federal=True)
        self.check_db_entries_processed(TEST_UID, central_query_count=5)
        eq_(len(self.env.husky_api.requests), 1)

    def test_delete_with_phones_ok(self):
        self.login = TEST_PHONE_LOGIN
        self.create_user(
            TEST_PHONE_USER_UID,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
        )
        self.create_user(TEST_ANOTHER_UID, TEST_ANOTHER_LOGIN)

        self.set_request_uid(TEST_PHONE_USER_UID)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_deletion_is_recorded_in_statbox(
            uid=TEST_PHONE_USER_UID,
            with_phones=True,
        )
        self.check_db_entries_processed(
            TEST_PHONE_USER_UID,
            shard_query_count=7,
        )
        self.check_another_users_db_entries_are_intact(
            TEST_ANOTHER_UID,
            TEST_ANOTHER_LOGIN,
        )
        self.check_deletion_recorded_in_historydb(
            TEST_PHONE_USER_UID,
            with_phones=True,
        )

    def test_error_delete_pdd_without_grants(self):
        self.alias_name = 'pdd'
        self.login = TEST_PDD_LOGIN
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
            TEST_ACCOUNT_DELETE_KINOPOISK_GRANT,
        ])
        self.create_user(
            TEST_PDD_UID,
            domid=1,
            domain=TEST_PDD_DOMAIN,
        )
        self.set_request_uid(TEST_PDD_UID)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_delete_with_blocking_sids_fails(self):
        blocked_uid = TEST_UID + 2
        self.login = 'blocked_login'
        self.create_user(
            blocked_uid,
            subscribed_to=[8] + list(BLOCKING_SIDS),
        )

        self.set_request_uid(blocked_uid)
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['account.has_blocking_sids'],
            ignore_order_for=['blocking_sids'],
            blocking_sids=list(BLOCKING_SIDS),
        )
        self.check_user_is_blocked_on_deletion(blocked_uid)
        self.check_social_profiles_not_deleted(TEST_UID)

    def test_error_delete_normal_without_grants(self):
        self.create_user(TEST_UID)
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
            TEST_ACCOUNT_DELETE_PDD_GRANT,
            TEST_ACCOUNT_DELETE_KINOPOISK_GRANT,
        ])

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_error_delete_kinopoisk_without_grants(self):
        self.create_user(
            TEST_KINOPOISK_UID,
            aliases={
                'kinopoisk': '100500',
            },
        )
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
            TEST_ACCOUNT_DELETE_PDD_GRANT,
        ])
        self.set_request_uid(TEST_KINOPOISK_UID)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_ok_delete_kinopoisk_with_specific_grant(self):
        self.alias_name = 'kinopoisk'
        self.login = '100500'
        self.create_user(
            TEST_KINOPOISK_UID,
        )
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
            TEST_ACCOUNT_DELETE_KINOPOISK_GRANT,
        ])

        self.set_request_uid(TEST_KINOPOISK_UID)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_deletion_is_recorded_in_statbox(uid=TEST_KINOPOISK_UID)
        self.check_db_entries_processed(
            TEST_KINOPOISK_UID,
            central_query_count=3,
        )
        self.check_deletion_recorded_in_historydb(TEST_KINOPOISK_UID)

    def test_ok_delete_social_without_global_grant(self):
        """
        Проверяем, что удаление социального аккаунта приведет к выбросу ошибке
        о нарушении доступа.
        """
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
        ])
        self.create_user(
            TEST_SOCIAL_UID,
            subscribed_to=[8, 58],
            aliases={
                'social': 'asdasd',
            },
        )
        self.set_request_uid(TEST_SOCIAL_UID)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_delete_social_profiles_fail(self):
        self.create_user(TEST_UID)
        self.env.social_api.set_response_side_effect(
            'delete_all_profiles_by_uid',
            RequestError(),
        )

        resp = self.make_request()
        self.assert_ok_response(resp)

    def test_family_info_admin(self):
        self.create_user(TEST_UID, family_info=TEST_FAMILY_INFO)
        self.create_family()

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries_processed(
            TEST_UID,
            central_query_count=6,
            shard_query_count=10,
        )
        self.check_db_family_deletion(
            TEST_FAMILY_ID,
            kid_uids=[TEST_KID_UID1, TEST_KID_UID2],
            member_uids=[TEST_UID, TEST_ANOTHER_UID],
        )
        self.check_deletion_recorded_in_historydb(
            TEST_UID,
            family_admin=True,
            kid_uids=[TEST_KID_UID1, TEST_KID_UID2],
            with_family=True,
        )
        self.check_deletion_is_recorded_in_statbox(
            family_admin=True,
            kid_uids=[TEST_KID_UID1, TEST_KID_UID2],
            with_family=True,
        )

    def test_family_info_not_admin(self):
        family_info = dict(TEST_FAMILY_INFO)
        family_info['admin_uid'] = TEST_ANOTHER_UID
        self.create_user(TEST_UID, family_info=family_info)
        self.create_family(admin_uid=TEST_ANOTHER_UID)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries_processed(TEST_UID, central_query_count=5)
        self.check_db_family_deletion(TEST_FAMILY_ID, [TEST_UID], is_admin=False)
        self.check_deletion_recorded_in_historydb(TEST_UID, with_family=True)
        self.check_deletion_is_recorded_in_statbox(with_family=True)

    def test_scholar_delete_ok(self):
        self.alias_name = 'scholar'
        self.login = TEST_SCHOLAR_LOGIN1
        self.scholar_password = '1:pwd'
        self.create_user(
            TEST_UID,
            attributes={'account.scholar_password': self.scholar_password},
        )
        self.create_user(TEST_ANOTHER_UID, TEST_ANOTHER_LOGIN)
        self.env.grants.set_grant_list([
            TEST_ACCOUNT_DELETE_BASE_GRANT,
            TEST_ACCOUNT_DELETE_SCHOLAR_GRANT,
        ])

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.check_deletion_is_recorded_in_statbox()
        self.check_db_entries_processed(TEST_UID)
        self.check_another_users_db_entries_are_intact(
            TEST_ANOTHER_UID,
            TEST_ANOTHER_LOGIN,
        )
        self.check_deletion_recorded_in_historydb(TEST_UID)


@nottest
class BaseTestAccountDeleteViewV2(BaseBundleTestViews):
    def setUp(self):
        super(BaseTestAccountDeleteViewV2, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'account': ['delete', 'delete_any']},
            },
        })

        self._track_manager = self.env.track_manager.get_manager()
        # Заранее созданный в ручке submit трек предназначен для всех ручек,
        # вызываемых после submit.
        self._track_id = self.env.track_manager.create_test_track(self._track_manager, 'authorize')
        with self._track_transaction() as track:
            track.process_name = 'account_delete_v2_process'
            track.uid = TEST_UID

        self._setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self._track_manager
        super(BaseTestAccountDeleteViewV2, self).tearDown()

    def _track_transaction(self):
        return self._track_manager.transaction(self._track_id).rollback_on_error()

    def _setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'internal',
            ip='127.0.0.1',
            user_agent='che',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'external',
            _inherit_from='internal',
            mode='account_delete',
            version='2',
        )
        self.env.statbox.bind_entry(
            'captcha.required',
            action='captcha_failed',
            mode='any_auth',
            track_id=self._track_id,
            ip='127.0.0.1',
            user_agent='che',
            yandexuid='yandexuid',
        )
        self.env.statbox.bind_entry('external', step=self.step_name, _inherit_from='external')
        self.env.statbox.bind_entry('submitted', action='submitted', _inherit_from='external')
        self.env.statbox.bind_entry(
            'set_disabled_status',
            event='account_modification',
            entity='account.disabled_status',
            operation='updated',
            old='enabled',
            new='disabled_on_deletion',
            uid=str(TEST_UID),
            ip='127.0.0.1',
            _inherit_from='internal',
        )
        self.env.statbox.bind_entry(
            'committed',
            action='committed',
            uid=str(TEST_UID),
            _inherit_from='external',
        )

    def _build_account(self, has_hint=False,
                       has_secure_phone=False, has_simple_phone=False,
                       has_not_suitable_email=False, has_password=True,
                       is_pdd=False, is_lite=False, has_suitable_email=False,
                       password_verification_required=False, is_fresh=False,
                       has_new_email=False, bound_date=None):
        userinfo = {
            'firstname': test_base_data.TEST_FIRSTNAME,
            'lastname': test_base_data.TEST_LASTNAME,
            'birthdate': test_base_data.TEST_BIRTHDAY,
        }
        if is_pdd:
            userinfo.update({
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'domain': TEST_PDD_DOMAIN,
                'aliases': {'pdd': TEST_PDD_LOGIN},
            })
        elif is_lite:
            userinfo.update({
                'uid': TEST_UID,
                'login': TEST_LOGIN,
                'aliases': {'lite': TEST_LOGIN},
            })
        else:
            userinfo.update({
                'uid': TEST_UID,
                'login': TEST_LOGIN,
            })
        if has_password:
            userinfo['crypt_password'] = '1:pwd'
        if has_hint:
            userinfo = deep_merge(
                userinfo,
                {
                    'dbfields': {
                        'userinfo_safe.hintq.uid': test_base_data.TEST_HINT_QUESTION,
                        'userinfo_safe.hinta.uid': test_base_data.TEST_HINT_ANSWER,
                    },
                },
            )
        if has_secure_phone:
            bound_date = bound_date or TEST_DATE
            userinfo = deep_merge(
                userinfo,
                build_phone_secured(
                    test_base_data.TEST_PHONE_ID1,
                    test_base_data.TEST_PHONE_NUMBER1.e164,
                    phone_bound=bound_date,
                    phone_created=bound_date,
                    phone_confirmed=bound_date,
                    phone_secured=bound_date,
                ),
            )
        if has_simple_phone:
            userinfo = deep_merge(
                userinfo,
                build_phone_bound(test_base_data.TEST_PHONE_ID2, test_base_data.TEST_PHONE_NUMBER.e164),
            )
        if has_suitable_email:
            userinfo = deep_merge(
                userinfo,
                {
                    'email_attributes': [
                        self._build_email(
                            test_base_data.TEST_EMAIL_ID1,
                            test_base_data.TEST_EXTERNAL_EMAIL1,
                            bound=datetime.now() - timedelta(days=8),
                        ),
                    ],
                },
            )
        if has_not_suitable_email:
            userinfo = deep_merge(
                userinfo,
                {
                    'email_attributes': [
                        self._build_email(
                            test_base_data.TEST_EMAIL_ID2,
                            test_base_data.TEST_EXTERNAL_EMAIL2,
                            bound=datetime.now() - timedelta(days=8),
                            # Этот адрес не подходит, потому что почта из него
                            # попадает в яндексовый ящик.
                            is_rpop=True,
                        ),
                    ],
                },
            )

        if has_new_email:
            userinfo = deep_merge(
                userinfo,
                {
                    'email_attributes': [
                        self._build_email(
                            test_base_data.TEST_EMAIL_ID1,
                            test_base_data.TEST_EXTERNAL_EMAIL1,
                            bound=datetime.now() - timedelta(days=2),
                        ),
                    ],
                },
            )

        if password_verification_required:
            password_verification_age = timedelta(hours=24).total_seconds()
        else:
            password_verification_age = 0
        sessionid = {
            'age': password_verification_age,
        }

        if is_fresh is not None:
            reg_date = date.today() if is_fresh else date.today() - timedelta(days=8)

            userinfo = deep_merge(
                userinfo,
                {
                    'dbfields': {
                        'userinfo.reg_date.uid': reg_date.strftime(DEFAULT_FORMAT),
                    },
                },
            )
        return {'userinfo': userinfo, 'sessionid': sessionid}

    def _setup_account(self, account):
        sessionid_args = deep_merge(account['userinfo'], account['sessionid'])
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_multi_response(**sessionid_args))

    def assert_ok_response(self, rv, **kwargs):
        kwargs.setdefault('track_id', self._track_id)
        kwargs.setdefault('account', self._get_response_about_account())
        return super(BaseTestAccountDeleteViewV2, self).assert_ok_response(rv, **kwargs)

    def _get_response_about_account(self):
        return {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'display_login': TEST_LOGIN,
            'display_name': {'name': '', 'default_avatar': ''},
            'person': {
                'firstname': test_base_data.TEST_FIRSTNAME,
                'lastname': test_base_data.TEST_LASTNAME,
                'birthday': test_base_data.TEST_BIRTHDAY,
                'gender': 1,
                'language': 'ru',
                'country': 'ru',
            },
        }

    def _get_response_about_pdd_account(self):
        return {
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'display_login': TEST_PDD_LOGIN,
            'display_name': {'name': '', 'default_avatar': ''},
            'person': {
                'firstname': test_base_data.TEST_FIRSTNAME,
                'lastname': test_base_data.TEST_LASTNAME,
                'birthday': test_base_data.TEST_BIRTHDAY,
                'gender': 1,
                'language': 'ru',
                'country': 'ru',
            },
            'domain': {'punycode': 'yandex.ru', 'unicode': 'yandex.ru'},
        }

    def _build_email(self, email_id, address, bound=None, is_rpop=False):
        email = {
            'id': email_id,
            'attributes': {
                EMAIL_ANT['address']: address,
                EMAIL_ANT['created']: 1,
                EMAIL_ANT['confirmed']: 3,
                EMAIL_ANT['is_rpop']: is_rpop,
            },
        }
        if bound:
            bound = datetime_to_integer_unixtime(bound)
            email['attributes'][EMAIL_ANT['bound']] = bound
        return email

    def test_bad_track__wrong_process_name(self):
        self._setup_account(self._build_account())

        with self._track_transaction() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self._make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_bad_track__no_process_name(self):
        self._setup_account(self._build_account())

        with self._track_transaction() as track:
            track.process_name = None

        rv = self._make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_bad_track__no_uid(self):
        self._setup_account(self._build_account())

        with self._track_transaction() as track:
            track.uid = None

        rv = self._make_request()

        self.assert_error_response(rv, ['track.invalid_state'], track_id=self._track_id)

    def test_bad_track__alien_uid(self):
        self._setup_account(self._build_account())

        with self._track_transaction() as track:
            track.uid = TEST_ANOTHER_UID

        rv = self._make_request()

        self.assert_error_response(rv, ['sessionid.no_uid'], track_id=self._track_id)

    requires_captcha = True

    def test_captcha_not_passed(self):
        if not self.requires_captcha:
            return

        with self._track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_recognized = False

        rv = self._make_request()

        self.assert_error_response(rv, ['captcha.required'], track_id=self._track_id)

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('captcha.required'),
        ])
        self.env.event_logger.assert_events_are_logged([])

        track = self._track_manager.read(self._track_id)
        ok_(track.is_captcha_required)


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestAccountDeleteCommitViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'commit'

    def setUp(self):
        super(TestAccountDeleteCommitViewV2, self).setUp()

        with self._track_transaction() as track:
            track.is_captcha_recognized = True
            track.is_captcha_checked = True

        self.ilahu_patch = mock.patch(
            'passport.backend.api.common.authorization.build_cookie_ilahu',
            mock.Mock(return_value=test_base_data.TEST_COOKIE_ILAHU),
        )
        self.ilahu_patch.start()

        self.mda2_beacon_patch = mock.patch(
            'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
            return_value=MDA2_BEACON_VALUE,
        )
        self.mda2_beacon_patch.start()

        self._setup_account(self._build_account())

    def tearDown(self):
        self.mda2_beacon_patch.stop()
        self.ilahu_patch.stop()
        del self.mda2_beacon_patch
        del self.ilahu_patch
        super(TestAccountDeleteCommitViewV2, self).tearDown()

    def _setup_statbox_templates(self):
        super(TestAccountDeleteCommitViewV2, self)._setup_statbox_templates()
        self.env.statbox.bind_entry('global_logout', _inherit_from=['global_logout', 'internal'])
        self.env.statbox.bind_entry(
            'cookie_remove',
            _inherit_from='external',
            action='cookie_remove',
        )

    def _build_account(self, has_hint=False, has_secure_phone=False, has_simple_phone=False,
                       has_not_suitable_email=False, has_suitable_email=False,
                       is_pdd=False, is_lite=False, password_verification_required=False, other_uid=None):
        account = super(TestAccountDeleteCommitViewV2, self)._build_account(
            has_hint=has_hint,
            has_secure_phone=has_secure_phone,
            has_simple_phone=has_simple_phone,
            has_not_suitable_email=has_not_suitable_email,
            has_suitable_email=has_suitable_email,
            is_pdd=is_pdd,
            is_lite=is_lite,
            password_verification_required=password_verification_required,
        )
        editsession = {
            'default_uid': other_uid or '',
            'session_value': '',
            'ssl_session_value': '',
        }
        return deep_merge(account, {'editsession': editsession})

    def _setup_account(self, account):
        sessionid_args = deep_merge(account['userinfo'], account['sessionid'])
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_multi_response(**sessionid_args))

        self.env.blackbox.set_response_value('editsession', blackbox_editsession_response(**account['editsession']))

    def _make_request(self):
        return self.env.client.post(
            '/2/bundle/delete_account/commit/',
            query_string={'consumer': 'dev'},
            data={'track_id': self._track_id},
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def _assert_deletion_started(self, uid=TEST_UID, shard='passportdbshard1'):
        self.env.db.check_db_attr(uid, 'account.is_disabled', str(ACCOUNT_DISABLED_ON_DELETION), db=shard)
        self.env.db.check_db_attr(uid, 'account.deletion_operation_started_at', TimeNow(), db=shard)
        self.env.db.check_line(
            'account_deletion_operations',
            {'deletion_id': 1, 'uid': uid, 'started_at': DatetimeNow()},
            db=shard,
        )

        track = self._track_manager.read(self._track_id)
        eq_(track.session, '')
        eq_(track.sslsession, '')

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('global_logout', uid=str(uid)),
            self.env.statbox.entry('set_disabled_status', uid=str(uid)),
            self.env.statbox.entry('cookie_remove', uid=str(uid)),
            self.env.statbox.entry('committed', uid=str(uid)),
        ])

        self.env.event_logger.assert_events_are_logged_with_order([
            {'name': 'info.ena', 'value': '0'},
            {'name': 'info.disabled_status', 'value': '2'},
            {'name': 'info.glogout', 'value': TimeNow()},
            {'name': 'deletion_operation', 'value': 'created'},
            {'name': 'action', 'value': 'account_delete'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'che'},
        ])

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                [
                    ('type', 'web'),
                    ('status', 'ses_kill'),
                    ('uid', str(uid)),
                    ('useragent', 'che'),
                    ('yandexuid', 'yandexuid'),
                    ('comment', 'aid=%s;ttl=0' % TEST_AUTH_ID),
                    ('ip_from', '127.0.0.1'),
                    ('client_name', 'passport'),
                ],
            ],
        )

    def assert_ok_response(self, rv, **kwargs):
        kwargs.setdefault(
            'cookies',
            [
                test_base_data.TEST_EMPTY_SESSIONID_COOKIE,
                test_base_data.TEST_EMPTY_SESSIONID2_COOKIE,
                EXPECTED_LONG_MDA2_BEACON_COOKIE,
                test_base_data.TEST_COOKIE_ILAHU,
                build_cookie_yp(None, current_yp_value='', display_name=None, domain='.yandex.ru'),
                build_cookie_ys(None, current_ys_value='', display_name=None, domain='.yandex.ru', samesite=''),
                build_cookie_yandex_login(env=Environment(host='passport.yandex.ru'), human_readable_login=None),
            ],
        )
        kwargs.setdefault('ignore_order_for', ['cookies'])
        return super(TestAccountDeleteCommitViewV2, self).assert_ok_response(rv, **kwargs)

    def test_only_password__password_not_required(self):
        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_only_password__password_required(self):
        self._setup_account(self._build_account(password_verification_required=True))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['password.required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_only_hint(self):
        self._setup_account(self._build_account(has_hint=True))
        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_only_hint__not_passed(self):
        self._setup_account(self._build_account(has_hint=True))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_suitable_email(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_suitable_email__has_hint(self):
        self._setup_account(self._build_account(has_hint=True, has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_suitable_email__not_confirmed(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_suitable_email__other_confirmed__from_account(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_not_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL2
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_suitable_email__other_confirmed__not_from_account(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL3
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_email__too_young(self):
        account = self._build_account()
        account['userinfo'] = deep_merge(
            account['userinfo'],
            dict(
                email_attributes=[
                    self._build_email(
                        test_base_data.TEST_EMAIL_ID1,
                        test_base_data.TEST_EXTERNAL_EMAIL1,
                        bound=datetime.now() - timedelta(days=6),
                    ),
                ],
            ),
        )
        self._setup_account(account)

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_has_email_and_hint(self):
        self._setup_account(self._build_account(has_hint=True, has_suitable_email=True))

        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_secure_phone(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_secure_phone__has_email(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_secure_phone=True))

        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_secure_phone__has_hint(self):
        self._setup_account(self._build_account(has_hint=True, has_secure_phone=True))

        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_secure_phone__not_confirmed(self):
        self._setup_account(self._build_account(has_secure_phone=True))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_secure_phone__other_confirmed(self):
        self._setup_account(self._build_account(has_secure_phone=True, has_simple_phone=True))
        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_secure_phone_too_young(self):
        account = self._build_account()
        account['userinfo'] = deep_merge(
            account['userinfo'],
            build_phone_secured(
                test_base_data.TEST_PHONE_ID1,
                test_base_data.TEST_PHONE_NUMBER1.e164,
                phone_created=datetime.now(),
                phone_bound=datetime.now(),
                phone_secured=datetime.now(),
                phone_confirmed=datetime.now(),
            ),
        )
        self._setup_account(account)

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_deletion_started()

    def test_has_phone_and_hint(self):
        self._setup_account(self._build_account(has_hint=True, has_secure_phone=True))

        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_has_phone_and_email(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_secure_phone=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['user.not_verified'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_pdd_admin(self):
        account = self._build_account()
        account['userinfo'] = deep_merge(
            account['userinfo'],
            dict(subscribed_to=[Service.by_slug('pddadmin')]),
        )
        self._setup_account(account)

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['unable_to_delete_pdd_admin'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_pdd_account(self):
        self._setup_account(self._build_account(is_pdd=True))

        with self._track_transaction() as track:
            track.uid = TEST_PDD_UID

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['unable_to_delete_pdd_account'],
            track_id=self._track_id,
            account=self._get_response_about_pdd_account(),
        )
        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_lite_account(self):
        self._setup_account(self._build_account(is_lite=True))

        rv = self._make_request()

        self.assert_ok_response(rv, account=self._get_response_about_account())
        self._assert_deletion_started()

    def test_several_users_in_multisession(self):
        self._setup_account(self._build_account(has_hint=True, other_uid=TEST_ANOTHER_UID))
        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_ok_response(rv, default_uid=TEST_ANOTHER_UID)
        self._assert_deletion_started()


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    ACCOUNT_FRESH_PERIOD=timedelta(days=7),
)
class TestAccountDeleteSubmitViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'submit'
    requires_captcha = False

    def _setup_account(self, account):
        sessionid_args = deep_merge(account['userinfo'], account['sessionid'])
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_multi_response(**sessionid_args))

    def _make_request(self):
        return self.env.client.post(
            '/2/bundle/delete_account/submit/',
            query_string={'consumer': 'dev'},
            data={'track_id': self._track_id},
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def assert_ok_response(self, rv, **kwargs):
        kwargs.setdefault('requirements', {})
        kwargs.setdefault('subscribed_to', [])
        return super(TestAccountDeleteSubmitViewV2, self).assert_ok_response(rv, **kwargs)

    def _assert_track_initialized(self, uid=TEST_UID):
        track = self._track_manager.read(self._track_id)
        ok_(type(track) is AuthTrack)
        eq_(track.process_name, PROCESS_ACCOUNT_DELETE_V2)
        eq_(track.uid, str(uid))
        ok_(track.is_captcha_required)

    def test_only_password__password_required(self):
        self._setup_account(self._build_account(password_verification_required=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={'password_required': None},
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_only_password__password_not_required(self):
        self._setup_account(self._build_account())

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_hint(self):
        self._setup_account(self._build_account(has_hint=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'question_required': {'question': {'id': 99, 'text': "Doroty's best friend"}},
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_password_and_hint_required(self):
        self._setup_account(self._build_account(password_verification_required=True, has_hint=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'password_required': None,
                'question_required': {'question': {'id': 99, 'text': "Doroty's best friend"}},
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_not_suitable_email(self):
        self._setup_account(self._build_account(has_not_suitable_email=True))

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_new_email_but_fresh_account(self):
        self._setup_account(self._build_account(has_new_email=True, is_fresh=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'email_required': {
                    'emails': [
                        {'address': test_base_data.TEST_EXTERNAL_EMAIL1},
                    ],
                },
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_suitable_email(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'email_required': {
                    'emails': [
                        {'address': test_base_data.TEST_EXTERNAL_EMAIL1},
                    ],
                },
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_simple_phone(self):
        self._setup_account(self._build_account(has_simple_phone=True))

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

    def test_secure_phone(self):
        self._setup_account(self._build_account(has_secure_phone=True, has_hint=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'phone_required': {
                    'phone': {
                        'id': test_base_data.TEST_PHONE_ID1,
                        'number': dump_number(test_base_data.TEST_PHONE_NUMBER1),
                        'is_alias': False,
                        'alias': {
                            'email_enabled': False,
                            'login_enabled': False,
                            'email_allowed': False,
                        },
                        'is_default': True,
                        'need_admission': True,
                        'created': datetime_to_integer_unixtime(TEST_DATE),
                        'bound': datetime_to_integer_unixtime(TEST_DATE),
                        'secured': datetime_to_integer_unixtime(TEST_DATE),
                        'confirmed': datetime_to_integer_unixtime(TEST_DATE),
                    },
                },
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_new_phone_and_old_account(self):
        bound_date = datetime.now()
        self._setup_account(self._build_account(has_secure_phone=True, bound_date=bound_date))

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_new_phone_and_super_old_account(self):
        bound_date = datetime.now()
        self._setup_account(self._build_account(has_secure_phone=True, bound_date=bound_date, is_fresh=None))

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_new_phone_and_new_account(self):
        bound_date = datetime.now()
        self._setup_account(self._build_account(has_secure_phone=True, bound_date=bound_date, is_fresh=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            requirements={
                'phone_required': {
                    'phone': {
                        'id': test_base_data.TEST_PHONE_ID1,
                        'number': dump_number(test_base_data.TEST_PHONE_NUMBER1),
                        'is_alias': False,
                        'alias': {
                            'email_enabled': False,
                            'login_enabled': False,
                            'email_allowed': False,
                        },
                        'is_default': True,
                        'need_admission': False,
                        'created': datetime_to_integer_unixtime(bound_date),
                        'bound': datetime_to_integer_unixtime(bound_date),
                        'secured': datetime_to_integer_unixtime(bound_date),
                        'confirmed': datetime_to_integer_unixtime(bound_date),
                    },
                },
            },
        )
        self._assert_track_initialized()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_subscriptions(self):
        account = self._build_account()
        services = [Service.by_slug('mail'), Service.by_slug('strongpwd'), Service.by_slug('balance')]
        account['userinfo'] = deep_merge(account['userinfo'], dict(subscribed_to=services))
        self._setup_account(account)

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            subscribed_to=[
                {
                    'sid': Service.by_slug('balance').sid,
                    'is_blocking': True,
                },
                # О strongpwd не сообщается, потому что он ненастоящий.
                {
                    'sid': Service.by_slug('mail').sid,
                    'is_blocking': False,
                },
            ],
        )
        self._assert_track_initialized()

    def test_reuse_good_track(self):
        self._setup_account(self._build_account())

        with self._track_transaction() as track:
            track.captcha_checked_at = '12345'

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

        track = self._track_manager.read(self._track_id)
        eq_(track.captcha_checked_at, '12345')

    def test_pdd_admin(self):
        account = self._build_account()
        account['userinfo'] = deep_merge(
            account['userinfo'],
            dict(subscribed_to=[Service.by_slug('pddadmin')]),
        )
        self._setup_account(account)

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['unable_to_delete_pdd_admin'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_connect_admin(self):
        account = self._build_account()
        account['userinfo'] = deep_merge(
            account['userinfo'],
            dict(attributes={'account.is_connect_admin': True}),
        )
        self._setup_account(account)

        rv = self._make_request()

        self.assert_ok_response(rv)

    def test_hint_answered(self):
        self._setup_account(self._build_account(has_hint=True))

        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

    def test_secure_phone_confirmed(self):
        self._setup_account(self._build_account(has_secure_phone=True))

        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_track_initialized()

    def test_inappropriate_account(self):
        self._setup_account(self._build_account(has_password=False))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['account.required_completion'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_pdd_account(self):
        self._setup_account(self._build_account(is_pdd=True))
        with self._track_transaction() as track:
            track.uid = TEST_PDD_UID

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['unable_to_delete_pdd_account'],
            track_id=self._track_id,
            account=self._get_response_about_pdd_account(),
        )
        self.env.db.assert_executed_queries_equal([])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_lite_account(self):
        self._setup_account(self._build_account(is_lite=True))

        rv = self._make_request()

        self.assert_ok_response(
            rv,
            account=self._get_response_about_account(),
        )
        self._assert_track_initialized()


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    **mock_counters(
        SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class TestAccountDeletePhoneSendCodeViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'send_phone_code'

    def setUp(self):
        super(TestAccountDeletePhoneSendCodeViewV2, self).setUp()

        with self._track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.code_generator.set_return_value(test_base_data.TEST_CONFIRMATION_CODE)
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def _setup_statbox_templates(self):
        super(TestAccountDeletePhoneSendCodeViewV2, self)._setup_statbox_templates()
        self.env.statbox.bind_entry(
            'send_confirmation_code.code_sent',
            action='send_confirmation_code.code_sent',
            _inherit_from='external',
            sms_id='1',
            sms_count='1',
            number=test_base_data.TEST_PHONE_NUMBER1.masked_format_for_statbox,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'send_confirmation_code.error',
            action='send_confirmation_code',
            _inherit_from='external',
            number=test_base_data.TEST_PHONE_NUMBER1.masked_format_for_statbox,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['external'],
            action='send_confirmation_code',
            antifraud_reason='some-reason',
            antifraud_tags='',
            number=test_base_data.TEST_PHONE_NUMBER1.masked_format_for_statbox,
            scenario='authorize',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )

    def _make_request(self):
        data = {
            'display_language': 'ru',
            'track_id': self._track_id,
        }
        return self.env.client.post(
            '/2/bundle/delete_account/send_sms/',
            query_string={'consumer': 'dev'},
            data=data,
            headers=self.build_headers(),
        )

    def build_headers(self):
        return {
            'Ya-Consumer-Client-Ip': '127.0.0.1',
            'Ya-Client-User-Agent': 'che',
            'Ya-Client-Host': 'passport.yandex.ru',
            'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
        }

    def _assert_sms_sent(self):
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.get_requests_by_method('send_sms')[0].assert_query_contains({
            'phone': test_base_data.TEST_PHONE_NUMBER1.e164,
        })

    def _assert_track_updated(self, phone=test_base_data.TEST_PHONE_NUMBER1.e164, is_confirmed=False,
                              sms_count=0, confirms_count=0, last_send_at=0, code=None):
        track = self._track_manager.read(self._track_id)

        eq_(track.phone_confirmation_phone_number, phone)
        eq_(track.phone_confirmation_is_confirmed, is_confirmed)
        eq_(track.phone_confirmation_sms_count.get(default=0), sms_count)
        eq_(track.phone_confirmation_confirms_count.get(default=0), confirms_count)
        eq_(track.phone_confirmation_last_send_at, last_send_at)
        eq_(track.phone_confirmation_code, code)

    def _assert_ok_pharma_request(self, request):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=test_base_data.TEST_PHONE_NUMBER1,
        )
        features.external_id = 'track-{}'.format(self._track_id)
        features.uid = TEST_UID
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = '/2/bundle/delete_account/send_sms/'
        features.scenario = 'authorize'
        features.add_headers_features(self.build_headers())
        assert request_data == features.as_score_dict()

    def test_phone_confirmed__action_not_required(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        with self._track_transaction() as track:
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        eq_(self.env.yasms.requests, [])

    def test_phone_not_available__action_not_required(self):
        self._setup_account(self._build_account(has_secure_phone=False))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        eq_(self.env.yasms.requests, [])

    def test_sms_per_ip_limit_exceeded(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        buckets = sms_per_ip.get_counter('127.0.0.1')
        for _ in range(buckets.limit):
            buckets.incr('127.0.0.1')

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self._assert_track_updated(is_confirmed=None, last_send_at=None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('send_confirmation_code.error', error='sms_limit.exceeded', reason='ip_limit'),
        ])

    def test_sms_rate_exceeded(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        last_send_at = str(int(time.time()))
        with self._track_transaction() as track:
            track.phone_confirmation_last_send_at = last_send_at
            track.phone_confirmation_is_confirmed = False

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self._assert_track_updated(last_send_at=last_send_at)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('send_confirmation_code.error', error='sms_limit.exceeded', reason='rate_limit'),
        ])

    def test_sms_sent__ok(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        rv = self._make_request()

        self.assert_ok_response(rv, resend_timeout=30)
        self._assert_sms_sent()
        self._assert_track_updated(
            sms_count=1,
            last_send_at=TimeNow(),
            code=test_base_data.TEST_CONFIRMATION_CODE,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('send_confirmation_code.code_sent'),
            self.env.statbox.entry('committed'),
        ])

    def test_sms_resent__ok(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        rv = self._make_request()

        self.assert_ok_response(rv, resend_timeout=30)
        self._assert_sms_sent()
        self._assert_track_updated(
            sms_count=2,
            last_send_at=TimeNow(),
            code=test_base_data.TEST_CONFIRMATION_CODE,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('send_confirmation_code.code_sent', sms_count='2'),
            self.env.statbox.entry('committed'),
        ])

    def test_phone_changed__sms_sent__ok(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE_1
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request()

        self.assert_ok_response(resp, resend_timeout=30)
        self._assert_sms_sent()
        self._assert_track_updated(
            phone=test_base_data.TEST_PHONE_NUMBER1.e164,
            sms_count=1,
            last_send_at=TimeNow(),
            code=test_base_data.TEST_CONFIRMATION_CODE,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('send_confirmation_code.code_sent', sms_count='1'),
            self.env.statbox.entry('committed'),
        ])

    def test_phone_changed__sms_not_sent__track_state_updated(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        self.env.yasms.set_response_side_effect(
            'send_sms',
            yasms_exceptions.YaSmsError('error message'),
        )
        last_send_at = int(time.time()) - 1000
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE_1
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_last_send_at = last_send_at
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['exception.unhandled'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self._assert_track_updated(
            # Номер сохранили, признак подтверждения, код, число смс сбросили
            phone=test_base_data.TEST_PHONE_NUMBER1.e164,
            last_send_at=str(last_send_at),
            code=None,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('send_confirmation_code.error', error='sms.isnt_sent'),
        ])

    def test_yasms_failures(self):
        self._setup_account(self._build_account(has_secure_phone=True))

        errors = [
            (
                yasms_exceptions.YaSmsError('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsAccessDenied('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsLimitExceeded('error message'),
                {u'reason': u'yasms_phone_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsPermanentBlock('error message'),
                {u'errors': [u'phone.blocked']},
                'phone.blocked',
            ),
            (
                yasms_exceptions.YaSmsTemporaryBlock('error message'),
                {u'reason': u'yasms_rate_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsUidLimitExceeded('error message'),
                {u'reason': u'yasms_uid_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsSecureNumberNotAllowed('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsSecureNumberExists('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsPhoneNumberValueError('error message'),
                {u'errors': [u'number.invalid']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsDeliveryError('error message'),
                {u'errors': [u'backend.yasms_failed']},
                'sms.isnt_sent',
            ),
        ]

        for index, (yasms_error, info, code) in enumerate(errors):
            with self._track_transaction() as track:
                track.phone_confirmation_code = None
                track.phone_confirmation_phone_number = None
                track.phone_confirmation_is_confirmed = False
                track.phone_confirmation_last_send_at = None
                track.phone_confirmation_sms_count.reset()
            self.env.yasms.set_response_side_effect('send_sms', yasms_error)

            resp = self._make_request()

            self.assert_error_response(
                resp,
                info['errors'],
                track_id=self._track_id,
                account=self._get_response_about_account(),
            )
            entry_kwargs = dict(error=code)
            if 'reason' in info:
                entry_kwargs['reason'] = info['reason']
            self.env.statbox.assert_contains(
                [
                    self.env.statbox.entry('send_confirmation_code.error', **entry_kwargs),
                ],
                offset=index * 2,
            )

    def test_pharma_denied(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self._assert_ok_pharma_request(self.env.antifraud_api.requests[0])


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    SMS_VALIDATION_MAX_CHECKS_COUNT=test_base_data.TEST_SMS_VALIDATION_MAX_CHECKS_COUNT,
)
class TestAccountDeleteConfirmPhoneViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'confirm_phone'

    def setUp(self):
        super(TestAccountDeleteConfirmPhoneViewV2, self).setUp()
        with self._track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

    def _setup_statbox_templates(self):
        super(TestAccountDeleteConfirmPhoneViewV2, self)._setup_statbox_templates()
        self.env.statbox.bind_entry(
            'phone_confirmed',
            number=test_base_data.TEST_PHONE_NUMBER1.masked_format_for_statbox,
            login=TEST_LOGIN,
            _exclude=['operation_id'],
            _inherit_from=['phone_confirmed', 'external'],
        )

    def _make_request(self, code=test_base_data.TEST_CONFIRMATION_CODE):
        data = {
            'code': code,
            'track_id': self._track_id,
        }
        return self.env.client.post(
            '/2/bundle/delete_account/confirm_phone/',
            query_string={'consumer': 'dev'},
            data=data,
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def test_code_was_not_sent(self):
        self._setup_account(self._build_account(has_secure_phone=True))

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['track.invalid_state'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])

    def test_phone_confirmed__action_not_required(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_phone_not_available__action_not_required(self):
        self._setup_account(self._build_account(has_secure_phone=False))
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = False

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_secure_phone_changed(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['phone.changed'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        track = self._track_manager.read(self._track_id)
        eq_(track.phone_confirmation_is_confirmed, False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru')
        ])

    def test_code_checks_limit_exceeded(self):
        self._setup_account(self._build_account(has_secure_phone=True))
        with self._track_transaction() as track:
            for _ in range(test_base_data.TEST_SMS_VALIDATION_MAX_CHECKS_COUNT):
                track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request()

        self.assert_error_response(
            resp,
            ['confirmations_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        track = self._track_manager.read(self._track_id)
        eq_(track.phone_confirmation_confirms_count.get(), test_base_data.TEST_SMS_VALIDATION_MAX_CHECKS_COUNT)
        eq_(track.phone_confirmation_is_confirmed, False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])

    def test_invalid_code(self):
        account = self._build_account(has_secure_phone=True)
        self._setup_account(account)
        build_account(db_faker=self.env.db, **account['userinfo'])

        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request(code=test_base_data.TEST_CONFIRMATION_CODE_1)

        self.assert_error_response(
            resp,
            ['code.invalid'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        assert_secure_phone_bound.check_db(self.env.db, TEST_UID, {'id': test_base_data.TEST_PHONE_ID1, 'confirmed': datetime(2014, 2, 26)})

        track = self._track_manager.read(self._track_id)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        eq_(track.phone_confirmation_is_confirmed, False)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_confirm_phone_passed(self):
        account = self._build_account(has_secure_phone=True)
        self._setup_account(account)
        build_account(db_faker=self.env.db, **account['userinfo'])

        with self._track_transaction() as track:
            track.phone_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = test_base_data.TEST_PHONE_NUMBER1.e164
            track.phone_confirmation_is_confirmed = False
            track.phone_confirmation_last_send_at = int(time.time()) - 1000
            track.phone_confirmation_sms_count.incr()

        resp = self._make_request()

        self.assert_ok_response(resp)

        assert_secure_phone_bound.check_db(self.env.db, TEST_UID, {'id': test_base_data.TEST_PHONE_ID1, 'confirmed': DatetimeNow()})

        track = self._track_manager.read(self._track_id)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        eq_(track.phone_confirmation_is_confirmed, True)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({
            'action': 'confirm_phone',
            'phone.1.action': 'changed',
            'phone.1.number': test_base_data.TEST_PHONE_NUMBER1.e164,
            'phone.1.confirmed': TimeNow(),
            'consumer': 'dev',
            'user_agent': 'che',
        })


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD=test_base_data.TEST_ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD,
)
class TestAccountDeleteCheckAnswerViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'check_answer'

    def setUp(self):
        super(TestAccountDeleteCheckAnswerViewV2, self).setUp()
        with self._track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

    def _make_request(self, answer=test_base_data.TEST_HINT_ANSWER):
        data = {
            'answer': answer,
            'track_id': self._track_id,
        }
        return self.env.client.post(
            '/2/bundle/delete_account/check_answer/',
            query_string={'consumer': 'dev'},
            data=data,
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def test_has_secure_phone__action_not_required(self):
        self._setup_account(self._build_account(has_secure_phone=True))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])

    def test_answer_checked__action_not_required(self):
        self._setup_account(self._build_account(has_hint=True))
        with self._track_transaction() as track:
            track.is_secure_hint_answer_checked = True

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])

    def test_correct_answer(self):
        self._setup_account(self._build_account(has_hint=True))

        rv = self._make_request()

        self.assert_ok_response(rv)
        track = self._track_manager.read(self._track_id)
        ok_(track.is_secure_hint_answer_checked)
        eq_(track.answer_checks_count.get(default=0), 0)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('committed'),
        ])

    def test_wrong_answer(self):
        self._setup_account(self._build_account(has_hint=True))

        rv = self._make_request(answer='bad answer')

        self.assert_error_response(
            rv,
            ['answer.not_matched'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
            is_captcha_required=False,
        )
        track = self._track_manager.read(self._track_id)
        ok_(not track.is_secure_hint_answer_checked)
        eq_(track.answer_checks_count.get(default=0), 1)
        ok_(track.is_captcha_required)
        ok_(track.is_captcha_checked)
        ok_(track.is_captcha_recognized)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])

    def test_wrong_answer__captcha_invalidated(self):
        self._setup_account(self._build_account(has_hint=True))
        with self._track_transaction() as track:
            for _ in range(test_base_data.TEST_ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD - 1):
                track.answer_checks_count.incr()

        rv = self._make_request(answer='bad answer')

        self.assert_error_response(
            rv,
            ['answer.not_matched'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
            is_captcha_required=True,
        )
        track = self._track_manager.read(self._track_id)
        ok_(not track.is_secure_hint_answer_checked)
        eq_(track.answer_checks_count.get(default=0), test_base_data.TEST_ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=3,
    PASSPORT_SUBDOMAIN='passport',
    translations=TEST_TRANSLATIONS,
    **mock_counters(
        VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER=(24, 3600, 4),
        VALIDATOR_EMAIL_SENT_PER_UID_COUNTER=(24, 3600, 40),
    )
)
class TestAccountDeleteSendEmailCodeViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'send_email_code'

    def setUp(self):
        super(TestAccountDeleteSendEmailCodeViewV2, self).setUp()
        self.env.code_generator.set_return_value(test_base_data.TEST_CONFIRMATION_CODE1)

    def _setup_statbox_templates(self):
        super(TestAccountDeleteSendEmailCodeViewV2, self)._setup_statbox_templates()
        self.env.statbox.bind_entry(
            'email_sent',
            action='email_sent',
            email=mask_email_for_statbox(test_base_data.TEST_EXTERNAL_EMAIL1),
            identity='confirmation_code_for_account_deletion',
            uid=str(TEST_UID),
            _inherit_from='external',
        )

    def _make_request(self, email=None):
        data = {
            'email': email or test_base_data.TEST_EXTERNAL_EMAIL1,
            'track_id': self._track_id,
        }
        return self.env.client.post(
            '/2/bundle/delete_account/send_email/',
            query_string={'consumer': 'dev'},
            data=data,
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def _EMAIL_BODY_RUSSIAN(self, firstname=None, portal_alias=None, confirmation_code=None):
        firstname = firstname or test_base_data.TEST_FIRSTNAME
        portal_alias = portal_alias or TEST_LOGIN
        confirmation_code = confirmation_code or test_base_data.TEST_CONFIRMATION_CODE1

        portal_alias = masked_login(portal_alias)
        return '''
<!doctype html>
<html>
<head>
<meta http-equiv="Content-Type"  content="text/html; charset=UTF-8" />
<title></title>
<style>
    .mail-address a,
    .mail-address a[href] {{
        text-decoration: none !important;
        color: #000000 !important;
    }}
</style>
</head>
<body>
<table cellpadding="0" cellspacing="0" align="center" width="770px">
  <tr>
    <td>
      <img alt="" height="36" src="https://logo.url/" style="margin-left: 30px; margin-bottom: 15px;" width="68">
      <table width="100%" cellpadding="0" cellspacing="0" align="center">
        <tr>
          <td>
            <p>Здравствуйте, {firstname}!</p>
            <p>Для подтверждения удаления аккаунта <b>{portal_alias}</b> на Яндексе, введите следующий код подтверждения на странице удаления:</p>
            <p>{confirmation_code}</p>
            <p>Срок действия кода &mdash; 3 часа с момента отправки сообщения.</p>
            <p>Если вы не запрашивали код для удаления аккаунта &mdash; это мог сделать злоумышленник.</p>
            <p>В таком случае:</p>
            <ul>
              <li><a href="https://passport.yandex.ru/restoration" target="_blank">восстановите доступ</a> к аккаунту;</li>
              <li><a href="https://passport.yandex.ru/profile" target="_blank">проверьте актуальность</a> привязанного номера телефона и почты для восстановления.</li>
            </ul>
            <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
          </td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" align="center">
        <tr><td></td></tr>
        <tr><td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки Яндекса Вы можете через <a href='https://feedback2.yandex.ru/'>форму обратной связи</a>.</td></tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
        '''.format(firstname=firstname, portal_alias=portal_alias, confirmation_code=confirmation_code)

    def _assert_confirmation_email_sent(self, email=None, confirmation_code=None):
        assert_email_message_sent(
            self.env.mailer,
            email or test_base_data.TEST_EXTERNAL_EMAIL1,
            u'Письмецо в конверте подожди не рви',
            self._EMAIL_BODY_RUSSIAN(confirmation_code=confirmation_code),
        )

    def _assert_track_updated(self, email=None, confirmation_code=None):
        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_address, email or test_base_data.TEST_EXTERNAL_EMAIL1)
        eq_(track.email_confirmation_code, confirmation_code or test_base_data.TEST_CONFIRMATION_CODE1)

    def _get_email_counter_value(self, uid=None, email=None):
        total_sent_bucket = get_buckets('email_validator:total_sent')
        mail_message_counter_id = '%d/%s' % (uid or TEST_UID, email or test_base_data.TEST_EXTERNAL_EMAIL1)
        return total_sent_bucket.get(mail_message_counter_id)

    def _set_email_counter_not_less_than(self, value=1, uid=None, email=None):
        total_sent_bucket = get_buckets('email_validator:total_sent')
        mail_message_counter_id = '%d/%s' % (uid or TEST_UID, email or test_base_data.TEST_EXTERNAL_EMAIL1)
        current = total_sent_bucket.get(mail_message_counter_id)
        while current < value:
            total_sent_bucket.incr(mail_message_counter_id)
            current += 1

    def test_ok(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        eq_(self._get_email_counter_value(), 0)

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_confirmation_email_sent()
        self._assert_track_updated()
        eq_(self._get_email_counter_value(), 1)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('email_sent'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_no_suitable_emails(self):
        self._setup_account(self._build_account(has_not_suitable_email=True))

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        eq_(self.env.mailer.messages, [])

        track = self._track_manager.read(self._track_id)
        ok_(not track.email_confirmation_address)
        ok_(not track.email_confirmation_code)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_many_suitable_emails(self):
        account = self._build_account(has_suitable_email=True, has_not_suitable_email=True)
        account['userinfo'] = deep_merge(
            account['userinfo'],
            {
                'email_attributes': [
                    self._build_email(
                        test_base_data.TEST_EMAIL_ID3,
                        test_base_data.TEST_EXTERNAL_EMAIL3,
                        bound=datetime.now() - timedelta(days=8),
                    ),
                ],
            },
        )
        self._setup_account(account)

        rv = self._make_request(email=test_base_data.TEST_EXTERNAL_EMAIL3)

        self.assert_ok_response(rv)
        self._assert_confirmation_email_sent(email=test_base_data.TEST_EXTERNAL_EMAIL3)
        self._assert_track_updated(email=test_base_data.TEST_EXTERNAL_EMAIL3)

    def test_suitable_email_confirmed(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_checks_count.reset()
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )
        eq_(self.env.mailer.messages, [])

    def test_email_not_exist(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        rv = self._make_request(email=test_base_data.TEST_EXTERNAL_EMAIL3)

        self.assert_error_response(
            rv,
            ['email.not_suitable'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_email_not_suitable(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_not_suitable_email=True))

        rv = self._make_request(email=test_base_data.TEST_EXTERNAL_EMAIL2)

        self.assert_error_response(
            rv,
            ['email.not_suitable'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_invalid_email_format(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        rv = self._make_request(email='yello')

        self.assert_error_response(rv, ['email.invalid'])

    def test_resend_confirmation_code(self):
        self._setup_account(self._build_account(has_suitable_email=True))
        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE2

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_confirmation_email_sent(confirmation_code=test_base_data.TEST_CONFIRMATION_CODE2)
        self._assert_track_updated(confirmation_code=test_base_data.TEST_CONFIRMATION_CODE2)

    def test_email_changed(self):
        account = self._build_account(has_suitable_email=True)
        account['userinfo'] = deep_merge(
            account['userinfo'],
            {
                'email_attributes': [
                    self._build_email(
                        test_base_data.TEST_EMAIL_ID3,
                        test_base_data.TEST_EXTERNAL_EMAIL3,
                        bound=datetime.now() - timedelta(days=8),
                    ),
                ],
            },
        )
        self._setup_account(account)

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL3
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE2
            track.email_confirmation_checks_count.reset()
            track.email_confirmation_checks_count.incr()

        rv = self._make_request()

        self.assert_ok_response(rv)

        self._assert_confirmation_email_sent()
        self._assert_track_updated()

        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_checks_count.get(default=0), 0)

    def test_not_suitable_email_confirmed__given_not_suitable(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_not_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL2
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE2
            track.email_confirmation_checks_count.reset()
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_passed_at = 1

        rv = self._make_request(email=test_base_data.TEST_EXTERNAL_EMAIL2)

        self.assert_error_response(
            rv,
            ['email.not_suitable'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_not_suitable_email_confirmed__given_suitable(self):
        self._setup_account(self._build_account(has_suitable_email=True, has_not_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL2
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE2
            track.email_confirmation_checks_count.reset()
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_passed_at = 1

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_confirmation_email_sent()
        self._assert_track_updated()

    def test_checks_count_hit_limit(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE2

            track.email_confirmation_checks_count.reset()
            for _ in range(3):
                track.email_confirmation_checks_count.incr()

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_confirmation_email_sent()
        self._assert_track_updated()

    def test_message_count_hit_limit(self):
        self._setup_account(self._build_account(has_suitable_email=True))
        self._set_email_counter_not_less_than(value=5)

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['email_messages_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )


@istest
@with_settings_hosts(
    EMAIL_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    PHONE_SUITABLE_FOR_ACCOUNT_DELETION_SINCE_TIME=timedelta(days=7),
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=3,
)
class TestAccountDeleteConfirmEmailViewV2(BaseTestAccountDeleteViewV2):
    step_name = 'confirm_email'

    def setUp(self):
        super(TestAccountDeleteConfirmEmailViewV2, self).setUp()

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL1
            track.email_confirmation_code = test_base_data.TEST_CONFIRMATION_CODE1

    def _setup_statbox_templates(self):
        super(TestAccountDeleteConfirmEmailViewV2, self)._setup_statbox_templates()
        self.env.statbox.bind_entry(
            'email_confirmed',
            event='account_modification',
            entity='account.emails',
            operation='updated',
            email_id='3201',
            confirmed_at=DatetimeNow(convert_to_datetime=True),
            old='*****@joe.us',
            new='*****@joe.us',
            uid=str(TEST_UID),
            ip='127.0.0.1',
            user_agent='che',
            consumer='dev',
            is_suitable_for_restore='1',
        )

    def _make_request(self, code=None):
        data = {
            'code': code or test_base_data.TEST_CONFIRMATION_CODE1,
            'track_id': self._track_id,
        }
        return self.env.client.post(
            '/2/bundle/delete_account/confirm_email/',
            query_string={'consumer': 'dev'},
            data=data,
            headers={
                'Ya-Consumer-Client-Ip': '127.0.0.1',
                'Ya-Client-User-Agent': 'che',
                'Ya-Client-Host': 'passport.yandex.ru',
                'Ya-Client-Cookie': test_base_data.TEST_USER_COOKIE,
            },
        )

    def _assert_email_confirmed(self):
        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_address, test_base_data.TEST_EXTERNAL_EMAIL1)
        eq_(track.email_confirmation_code, test_base_data.TEST_CONFIRMATION_CODE1)
        eq_(track.email_confirmation_checks_count.get(default=0), 1)
        eq_(track.email_confirmation_passed_at, TimeNow())

        self.env.db.check_db_ext_attr(TEST_UID, EXTENDED_ATTRIBUTES_EMAIL_TYPE, test_base_data.TEST_EMAIL_ID1, 'confirmed', TimeNow())

    def test_correct_code(self):
        account = self._build_account(has_suitable_email=True)
        self._setup_account(account)
        build_account(db_faker=self.env.db, **account['userinfo'])

        rv = self._make_request()

        self.assert_ok_response(rv)
        self._assert_email_confirmed()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('email_confirmed'),
            self.env.statbox.entry('committed'),
        ])
        self.env.event_logger.assert_events_are_logged({
            'action': 'confirm_email',
            'email.3201': 'updated',
            'email.3201.address': test_base_data.TEST_EXTERNAL_EMAIL1,
            'email.3201.confirmed_at': TimeNow(),
            'consumer': 'dev',
            'user_agent': 'che',
        })

    def test_wrong_code(self):
        account = self._build_account(has_suitable_email=True)
        self._setup_account(account)
        build_account(db_faker=self.env.db, **account['userinfo'])

        with self._track_transaction() as track:
            track.email_confirmation_checks_count.reset()
            track.email_confirmation_checks_count.incr()

        rv = self._make_request(code=test_base_data.TEST_CONFIRMATION_CODE2)

        self.assert_error_response(
            rv,
            ['code.invalid'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_address, test_base_data.TEST_EXTERNAL_EMAIL1)
        eq_(track.email_confirmation_code, test_base_data.TEST_CONFIRMATION_CODE1)
        eq_(track.email_confirmation_checks_count.get(default=0), 2)
        ok_(not track.email_confirmation_passed_at)

        self.env.db.check_db_ext_attr(TEST_UID, EXTENDED_ATTRIBUTES_EMAIL_TYPE, test_base_data.TEST_EMAIL_ID1, 'confirmed', '3')

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
        ])
        self.env.event_logger.assert_events_are_logged({})

    def test_no_suitable_email(self):
        self._setup_account(self._build_account())

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_checks_count.get(default=0), 0)

    def test_email_not_suitable(self):
        self._setup_account(self._build_account(has_not_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = test_base_data.TEST_EXTERNAL_EMAIL2

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['action.not_required'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_checks_count.get(default=0), 0)

    def test_track_has_no_email(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_address = None

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['email.not_suitable'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_track_has_no_code(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_code = None

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

    def test_code_checks_hit_limit(self):
        self._setup_account(self._build_account(has_suitable_email=True))

        with self._track_transaction() as track:
            track.email_confirmation_checks_count.reset()
            for _ in range(3):
                track.email_confirmation_checks_count.incr()

        rv = self._make_request()

        self.assert_error_response(
            rv,
            ['email_confirmations_limit.exceeded'],
            track_id=self._track_id,
            account=self._get_response_about_account(),
        )

        track = self._track_manager.read(self._track_id)
        eq_(track.email_confirmation_checks_count.get(default=0), 3)
