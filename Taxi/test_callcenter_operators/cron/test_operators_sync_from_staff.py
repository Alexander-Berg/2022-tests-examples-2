# pylint: disable=C0302
import datetime
import json

import aiohttp
import pytest
import pytz

from test_callcenter_operators import test_utils


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_no_change_if_not_changed_in_staff(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles',
    )
    assert cursor.fetchall() == [
        ('uid1', 'operator', 'admin'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_update_first_name_middle_name_last_name(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'new_name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'new_surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'new_middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'new_name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'new_surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'new_middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles',
    )
    assert cursor.fetchall() == [
        ('uid1', 'operator', 'admin'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_update_phone_number_and_telegram(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+new_number', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'new_telega', 'private': False},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+new_number',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_order_of_response_of_staff_not_important(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login3',
                    'uid': 'some_uid',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'some_uid',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login1',
                    'uid': 'some_uid',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {
            'url_for_callcenter_random_cc': {'callcenter_id': 'random_cc'},
            'url_for_callcenter_special_callcenter': {
                'callcenter_id': 'special_callcenter',
            },
        },
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_only_2_operators.psql'],
)
async def test_sync_of_callcenter_id(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_random_cc',
                    },
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_special_callcenter',
                    },
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'special_callcenter',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': [
                'one_metaqueue',
                'second_metaqueue',
                'third_metaqueue',
            ],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {
            'url_for_callcenter_random_cc': {'callcenter_id': 'random_cc'},
            'url_for_callcenter_special_callcenter': {
                'callcenter_id': 'special_callcenter',
            },
        },
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'special_callcenter': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Minsk',
            'default_metaqueues': ['one_metaqueue', 'second_metaqueue'],
        },
        'random_cc': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'default_metaqueues': [
                'third_metaqueue',
                'fourth_second_metaqueue',
            ],
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_another', 'allowed_clusters': ['1']},
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'second_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'third_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'fourth_second_metaqueue', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_SIP_OPTIONS={
        'answerTimer': 1000,
        'chainIdHeader': 'X-TC-GUID',
        'domainToSip': {'by': ['reg3', 'reg4'], 'ru': ['reg1', 'reg2']},
        'originalDNHeader': 'X-CC-OriginalDN',
        'port': 7443,
        'stunServers': ['stun:141.8.146.81:3478'],
        'urls': {'by': 'yandex.ru', 'ru': 'yandex.ru'},
        'volume': 0.7,
        'websocketConnectionTimeout': 4000,
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_sync_metaqueues_when_sync_cc(
        cron_runner,
        cron_context,
        pgsql,
        mock_staff,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        web_context,
        mock_callcenter_queues,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_random_cc',
                    },
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_special_callcenter',
                    },
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    assert cursor.fetchall() == [
        (0, 'paused', 'tech', ['test']),
        (1, 'disconnected', None, ['test_another']),
        (2, 'connected', None, ['test']),
    ]

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony, timezone '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid2',
            'login2',
            'special_callcenter',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (0, 'paused', 'tech', ['test']),
        (1, 'disconnected', None, ['test_another']),
        (2, 'connected', None, ['one_metaqueue', 'second_metaqueue']),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {
            'url_for_callcenter_random_cc': {'callcenter_id': 'random_cc'},
            'url_for_callcenter_special_callcenter': {
                'callcenter_id': 'special_callcenter',
            },
        },
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'special_callcenter': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Minsk',
            'default_metaqueues': ['one_metaqueue', 'second_metaqueue'],
        },
        'random_cc': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'default_metaqueues': [
                'third_metaqueue',
                'fourth_second_metaqueue',
            ],
        },
    },
    CALLCENTER_METAQUEUES=[],  # empty
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_revert_sync_cc_if_error_in_change_metaqueues(
        cron_runner,
        cron_context,
        pgsql,
        mock_staff,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        web_context,
        mock_callcenter_queues,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_random_cc',
                    },
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_for_callcenter_special_callcenter',
                    },
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    assert cursor.fetchall() == [
        (0, 'paused', 'tech', ['test']),
        (1, 'disconnected', None, ['test_another']),
        (2, 'connected', None, ['test']),
    ]

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony, timezone '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (0, 'paused', 'tech', ['test']),
        (1, 'disconnected', None, ['test_another']),
        (2, 'connected', None, ['test']),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Minsk',
        },
        'random_cc': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_only_2_operators.psql'],
)
async def test_sync_of_timezone(cron_runner, cron_context, pgsql, mock_staff):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony, timezone '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',  # not changed
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Minsk',  # changed
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {
            'yandex_dep37494': {'callcenter_id': 'new_cc'},
        },
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_only_2_operators.psql'],
)
async def test_sync_callcenter_id_from_ancestors_staff_groups(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_of_user_department_group',
                        'ancestors': [
                            {'url': 'yandex'},
                            {
                                'url': 'yandex_dep37494',
                            },  # sync callcent_id from this url
                        ],
                    },
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                    'department_group': {
                        'url': 'url_of_user_department_group',
                        'ancestors': [
                            {'url': 'yandex'},
                            {'url': 'yandex_level_2'},
                        ],
                    },
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony, timezone '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'new_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
            'Europe/Moscow',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_staff_return_less_accounts(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enable': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_batch_db_request(cron_runner, cron_context, pgsql, mock_staff):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        logins_in_request = request.query['login'].split(',')
        body = {'result': []}

        if 'login1' in logins_in_request:
            body['result'].append(
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            )
        if 'login2' in logins_in_request:
            body['result'].append(
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            )
        if 'login3' in logins_in_request:
            body['result'].append(
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            )
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles',
    )
    assert cursor.fetchall() == [
        ('uid1', 'operator', 'admin'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': True,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_staff_return_empty_middle_name(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name1'},
                        'last': {'ru': 'surname1'},
                        'middle': '',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'surname2'},
                        'middle': '',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': '',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            None,  # not changed
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2021, 6, 22, 22, 10, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'enabled': False,
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_when_disabled_no_changes(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'new_name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'new_surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'new_middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles',
    )
    assert cursor.fetchall() == [
        ('uid1', 'operator', 'admin'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]


@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['yandex-team.ru'],
    CALLCENTER_OPERATORS_STAFF_SYNC={
        'map_staff_id_to_callcenter': {},
        'max_logins_per_staff_request': 100,
        'max_operators_per_db_request': 1000,
        'fields_for_update': [
            'first_name',
            'middle_name',
            'last_name',
            'telegram_login',
            'phone',
            'callcenter_id',
            'timezone',
            'default_metaqueues',
        ],
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth.psql'])
async def test_when_no_enable_in_config(
        cron_runner, cron_context, pgsql, mock_staff,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {
            'result': [
                {
                    'login': 'login1',
                    'uid': 'uid1',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+1', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'new_name1'},
                        'last': {'ru': 'surname1'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login2',
                    'uid': 'uid2',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+2', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name2'},
                        'last': {'ru': 'new_surname2'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
                {
                    'login': 'login3',
                    'uid': 'uid3',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '+3', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'name3'},
                        'last': {'ru': 'surname3'},
                        'middle': 'new_middle_name',
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    await cron_runner.operators_sync_from_staff()

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, yandex_login, callcenter_id, first_name, '
        'middle_name, last_name, created_at, deleted_at, updated_at, state, '
        'password, supervisor_login, phone_number, working_domain, '
        'operator_id, staff_login, staff_login_state, mentor_login, '
        'employment_date, name_in_telephony '
        'FROM callcenter_auth.operators_access '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        (
            'uid1',
            'login1',
            'random_cc',
            'name1',
            None,
            'surname1',
            datetime.datetime(
                2018, 6, 21, 23, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+1',
            'yandex-team.ru',
            1000000000,
            None,
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid2',
            'login2',
            'cc1',
            'name2',
            None,
            'surname2',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+2',
            'yandex-team.ru',
            1000000001,
            'staff_login2',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid3',
            'login3',
            'another_random_cc',
            'name3',
            'middle_name',
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000002,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_deleted',
            'login_deleted',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'deleted',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'yandex-team.ru',
            1000000003,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
        (
            'uid_not_internal_domain',
            'login_not_internal_domain',
            'another_random_cc',
            'name3',
            None,
            'surname3',
            datetime.datetime(
                2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            None,
            datetime.datetime(
                2018, 6, 22, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
            ),
            'ready',
            'DBg+FwQTGD4XBB4WOBoLUg==',
            'admin@unit.test',
            '+3',
            'not-yandex-team.ru',
            1000000004,
            'not_staff_login3',
            'unverified',
            None,
            datetime.date(2018, 6, 21),
            'tel_name',
        ),
    ]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles',
    )
    assert cursor.fetchall() == [
        ('uid1', 'operator', 'admin'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]
