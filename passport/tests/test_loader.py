# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.ufo_api.faker import (
    FakeUfoApi,
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.env_profile.loader import (
    load_ufo_profile,
    uuid1,
)
from passport.backend.core.env_profile.tests.base_test_data import UATRAITS_SETTINGS
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.ydb.faker.stubs import (
    FakeResultSet,
    ydb_profile_item,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.utils.time import datetime_to_integer_unixtime
import six


TEST_COVERED_UID = 49


@with_settings(
    UFO_API_URL='http://localhost/',
    UFO_API_TIMEOUT=1,
    UFO_API_RETRIES=2,
    UFO_API_USE_RC=False,
    TRY_USE_YDB=False,
    YDB_PERCENTAGE=0,
    **UATRAITS_SETTINGS
)
class TestLoadUfoProfile(unittest.TestCase):
    def setUp(self):
        self.ufo_api = FakeUfoApi()
        self.ufo_api.start()

        self.ydb = FakeYdb()
        self.ydb.start()

    def tearDown(self):
        self.ydb.stop()
        self.ufo_api.stop()
        del self.ydb
        del self.ufo_api

    def test_ufo_load(self):
        self.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[ufo_api_profile_item()]),
        )
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item())}])])

        kind, status, profile = load_ufo_profile(TEST_COVERED_UID)

        ok_(status)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts=1446212433 uuid=cb78b616-7f0b-11e5-b8cc-fc7bfc3c8e01>',
        )
        eq_(len(self.ufo_api.requests), 1)
        eq_(self.ydb.executed_queries(), [])

    def test_ufo_load_force(self):
        self.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[ufo_api_profile_item()]),
        )
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item())}])])

        kind, status, profile = load_ufo_profile(TEST_COVERED_UID, force_ydb=True)

        ok_(status)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts=1446212433 uuid=cae45e80-7f0b-11e5-8000-000000000000>',
        )
        eq_(len(self.ufo_api.requests), 0)
        eq_(
            self.ydb.executed_queries(),
            [{
                'query': (
                    'declare $uid as Uint64;\n'
                    'select value from [profile-testing] where uid = $uid LIMIT 51;\n'
                ),
                'parameters': {'$uid': TEST_COVERED_UID},
                'commit_tx': True,
            }],
        )


@with_settings(
    UFO_API_URL='http://localhost/',
    UFO_API_TIMEOUT=1,
    UFO_API_RETRIES=2,
    UFO_API_USE_RC=False,
    TRY_USE_YDB=True,
    YDB_PERCENTAGE=50,
    **UATRAITS_SETTINGS
)
class TestLoadYdbProfile(unittest.TestCase):
    def setUp(self):
        self.ufo_api = FakeUfoApi()
        self.ufo_api.start()

        self.ydb = FakeYdb()
        self.ydb.start()

    def tearDown(self):
        self.ydb.stop()
        self.ufo_api.stop()
        del self.ydb
        del self.ufo_api

    def test_ydb_load(self):
        self.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[ufo_api_profile_item()]),
        )
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item())}])])

        statbox_mock = mock.Mock()
        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            statbox=statbox_mock,
            statbox_context={'a': 1},
        )

        if six.PY2:
            expected_ydb_profile_items = (
                "[{u'timestamp': 1446212433, u'yandexuid': u'3281059040000000099', u'user_agent_info': "
                "{u'OSFamily': u'Java', u'BrowserEngine': u'Presto', u'isBrowser': True, "
                "u'BrowserVersion': u'6.5', u'BrowserName': u'OperaMini', u'BrowserEngineVersion': "
                "u'2.8.119', u'J2ME': True, u'isMobile': True}, u'ip': u'5.45.207.254'}]"
            )
        else:
            expected_ydb_profile_items = (
                "[{'ip': '5.45.207.254', "
                "'yandexuid': '3281059040000000099', 'user_agent_info': {'OSFamily': 'Java', "
                "'BrowserEngine': 'Presto', 'isBrowser': True, 'BrowserVersion': '6.5', 'BrowserName': 'OperaMini', "
                "'BrowserEngineVersion': '2.8.119', 'J2ME': True, 'isMobile': True}, 'timestamp': 1446212433}]"
            )
        statbox_mock.log.assert_called_once_with(
            a=1,
            ydb_profile_items=expected_ydb_profile_items,
        )
        ok_(status)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts=1446212433 uuid=cae45e80-7f0b-11e5-8000-000000000000>',
        )
        eq_(len(self.ufo_api.requests), 0)
        eq_(
            self.ydb.executed_queries(),
            [{
                'query': (
                    'declare $uid as Uint64;\n'
                    'select value from [profile-testing] where uid = $uid LIMIT 51;\n'
                ),
                'parameters': {'$uid': TEST_COVERED_UID},
                'commit_tx': True,
            }],
        )

    def test_ydb_load_from_datetime_fresh_profile_ok(self):
        # считаем что глогаут был час назад, запрашиваем профили, в профиле текущий таймстемп, должен вернуться профиль
        now = datetime.today()
        now_unixtime = datetime_to_integer_unixtime(now)
        now_timeuuid = str(uuid1(now_unixtime * 10 ** 9, unique_id=0))  # в uuid наносекунды
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item(timestamp=now_unixtime))}])])

        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            from_datetime=now - timedelta(hours=1),
        )
        ok_(status)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts={} uuid={}>'.format(now_unixtime, now_timeuuid),
        )
        eq_(profile.full_profile, None)

    def test_ydb_load_from_datetime_fresh_profile_outdated(self):
        # считаем что глогаут был сейчас, запрашиваем профили, в профиле таймстемп час назад, должен вернуться пустой список
        now = datetime.today()
        unixtime_hour_ago = datetime_to_integer_unixtime(now - timedelta(hours=1))
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item(timestamp=unixtime_hour_ago))}])])

        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            from_datetime=now,
        )
        ok_(status)
        fresh_profiles = list(profile.fresh_profiles)
        eq_(len(fresh_profiles), 0)
        eq_(profile.full_profile, None)

    def test_ydb_load_from_datetime_full_profile_ok(self):
        # считаем что глогаут был час назад, запрашиваем профили, в профиле текущий таймстемп, должен вернуться полный профиль
        now = datetime.today()
        now_unixtime = datetime_to_integer_unixtime(now)
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item(timestamp=now_unixtime, set_full_profile_flag=True))}])])

        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            from_datetime=now - timedelta(hours=1),
        )
        ok_(status)
        eq_(len(list(profile.fresh_profiles)), 0)
        eq_(
            profile.full_profile['timestamp'],
            now_unixtime,
        )

    def test_ydb_load_from_datetime_full_profile_outdated(self):
        # считаем что глогаут был сейчас, запрашиваем профили, в профиле таймстемп час назад, должен вернуться пустой список
        now = datetime.today()
        unixtime_hour_ago = datetime_to_integer_unixtime(now - timedelta(hours=1))
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(ydb_profile_item(timestamp=unixtime_hour_ago, set_full_profile_flag=True))}])])

        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            from_datetime=now,
        )
        ok_(status)
        eq_(len(list(profile.fresh_profiles)), 0)
        eq_(profile.full_profile, None)

    def test_ydb_load_from_datetime_profile_without_date(self):
        # если дата в профиле из ydb передана не была, он всегда вернется (для совместимости со старой системой записи профилей без даты)
        now = datetime.today()
        profile = ydb_profile_item()
        del profile['timestamp']
        self.ydb.set_execute_return_value([FakeResultSet([{'value': json.dumps(profile)}])])

        kind, status, profile = load_ufo_profile(
            TEST_COVERED_UID,
            from_datetime=now,
        )
        ok_(status)
        eq_(len(list(profile.fresh_profiles)), 1)
        eq_(profile.full_profile, None)
