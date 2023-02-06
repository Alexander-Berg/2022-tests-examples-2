# pylint: disable=redefined-outer-name
from typing import Dict

import pytest

from testsuite.databases.pgsql import control

from chatterbox import constants
from test_chatterbox import plugins as conftest


def get_db_status(current_status: str) -> tuple:
    if current_status.endswith('-in-additional'):
        in_additional = True
        db_current_status = current_status.split('-in-additional')[0]
    else:
        in_additional = False
        db_current_status = current_status
    return db_current_status, in_additional


@pytest.mark.translations(
    chatterbox={
        'status.offline': {'ru': 'Офлай', 'en': 'Offline'},
        'status.online': {'ru': 'Онлайн', 'en': 'Online'},
        'status.online_in_additional': {
            'ru': 'В доп.',
            'en': 'Online (in additional)',
        },
        'status.before_break': {'ru': 'Перед перерывом', 'en': 'Before break'},
        'status.online_reversed': {
            'ru': 'Онлайн в обратном порядке',
            'en': 'Online reversed',
        },
        'status.online_reversed_in_additional': {
            'ru': 'Онлайн в обратном порядке (В доп.)',
            'en': 'Online reversed (in additional)',
        },
        'status.break': {'ru': 'Перерыв', 'en': 'Break'},
        'status.training': {'ru': 'Тренинг', 'en': 'Training'},
        'status.feedback': {'ru': 'Обратная связь', 'en': 'Feedback'},
        'status.technical_problems': {
            'ru': 'Технические проблемы',
            'en': 'Technical problems',
        },
    },
)
@pytest.mark.parametrize(
    ('locale', 'translations'),
    (
        (
            'en',
            {
                'offline': 'Offline',
                'online': 'Online',
                'online_in_additional': 'Online (in additional)',
                'before_break': 'Before break',
                'online-reversed': 'Online reversed',
                'online-reversed-in-additional': (
                    'Online reversed (in additional)'
                ),
                'break': 'Break',
                'training': 'Training',
                'feedback': 'Feedback',
                'technical_problems': 'Technical problems',
            },
        ),
        (
            'ru',
            {
                'offline': 'Офлай',
                'online': 'Онлайн',
                'online_in_additional': 'В доп.',
                'before_break': 'Перед перерывом',
                'online-reversed': 'Онлайн в обратном порядке',
                'online-reversed-in-additional': (
                    'Онлайн в обратном порядке (В доп.)'
                ),
                'break': 'Перерыв',
                'training': 'Тренинг',
                'feedback': 'Обратная связь',
                'technical_problems': 'Технические проблемы',
            },
        ),
        (
            'az',
            {
                'offline': 'Offline',
                'online': 'Online',
                'online_in_additional': 'Online (in additional)',
                'before_break': 'Before break',
                'online-reversed': 'Online reversed',
                'online-reversed-in-additional': (
                    'Online reversed (in additional)'
                ),
                'break': 'Break',
                'training': 'Training',
                'feedback': 'Feedback',
                'technical_problems': 'Technical problems',
            },
        ),
    ),
)
async def test_user_status_translations(
        cbox: conftest.CboxWrap,
        patch,
        locale: str,
        translations: Dict[str, str],
):
    @patch('chatterbox.api.user_utils.get_available_change_for_status')
    def _get_available_change_for_status(*args) -> tuple:
        return tuple(constants.SUPPORT_STATUSES)

    expected_status_list = [
        {
            'can_work': False,
            'id': 'offline',
            'in_addition': False,
            'label': translations['offline'],
        },
        {
            'can_work': False,
            'id': 'before-break',
            'in_addition': False,
            'label': translations['before_break'],
        },
        {
            'can_work': False,
            'id': 'before-break-in-additional',
            'in_addition': True,
            'label': translations['before_break'],
        },
        {
            'can_work': True,
            'id': 'online',
            'in_addition': False,
            'label': translations['online'],
        },
        {
            'can_work': True,
            'id': 'online-in-additional',
            'in_addition': True,
            'label': translations['online_in_additional'],
        },
        {
            'can_work': True,
            'id': 'online-reversed',
            'in_addition': False,
            'label': translations['online-reversed'],
        },
        {
            'can_work': True,
            'id': 'online-reversed-in-additional',
            'in_addition': True,
            'label': translations['online-reversed-in-additional'],
        },
        {
            'can_work': False,
            'id': 'break',
            'in_addition': False,
            'label': translations['break'],
        },
        {
            'can_work': False,
            'id': 'training',
            'in_addition': False,
            'label': translations['training'],
        },
        {
            'can_work': False,
            'id': 'feedback',
            'in_addition': False,
            'label': translations['feedback'],
        },
        {
            'can_work': False,
            'id': 'technical_problems',
            'in_addition': False,
            'label': translations['technical_problems'],
        },
    ]

    await cbox.query('/v1/user/status', headers={'Accept-Language': locale})
    assert cbox.status == 200
    assert cbox.body_data['status_list'] == expected_status_list

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'offline', 'lines': ['first']},
        headers={'Accept-Language': locale},
    )
    assert cbox.status == 200
    assert cbox.body_data['status_list'] == expected_status_list
    assert cbox.body_data['next_request_timeout'] == 60000


@pytest.mark.parametrize('current_status', tuple(constants.SUPPORT_STATUSES))
async def test_user_default_work_status(
        cbox: conftest.CboxWrap,
        patch_auth,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        current_status: str,
        support_metrics_mock,
):
    db_current_status, in_additional = get_db_status(current_status)
    if in_additional:
        default_work_status = constants.STATUS_ONLINE_IN_ADDITIONAL
    else:
        default_work_status = constants.STATUS_ONLINE
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', db_current_status, ['second'], in_additional),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert cbox.body_data['default_work_status'] == default_work_status

    await cbox.post(
        '/v1/user/status',
        data={'current_status': current_status, 'lines': ['first']},
    )
    assert cbox.status == 200
    assert cbox.body_data['default_work_status'] == default_work_status


@pytest.mark.parametrize('current_status', tuple(constants.SUPPORT_STATUSES))
@pytest.mark.parametrize('incoming_calls_permitted', (True, False))
async def test_user_status_incoming_calls(
        cbox: conftest.CboxWrap,
        patch_auth,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        current_status: str,
        incoming_calls_permitted: bool,
        support_metrics_mock,
):
    groups = [
        'chatterbox_reversed_status',
        'chatterbox_extended_offline_statuses',
    ]
    if incoming_calls_permitted:
        groups.append('incoming_calls_permitted')
    patch_auth(superuser=False, groups=groups)

    db_current_status, in_additional = get_db_status(current_status)
    incoming_calls_enabled = (
        bool(current_status in constants.STATUSES_INCOMING_CALL_ENABLED)
        and incoming_calls_permitted
    )

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', db_current_status, ['second'], in_additional),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert cbox.body_data['incoming_calls_allowed'] == incoming_calls_enabled

    await cbox.post(
        '/v1/user/status',
        data={'current_status': current_status, 'lines': ['first']},
    )
    assert cbox.status == 200
    assert cbox.body_data['incoming_calls_allowed'] == incoming_calls_enabled


def assert_reversed_status(body: dict, reversed_permitted: bool) -> None:
    statuses = {status['id'] for status in body['status_list']}
    if reversed_permitted:
        assert constants.STATUS_ONLINE_REVERSED in statuses
        assert constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL in statuses
    else:
        assert constants.STATUS_ONLINE_REVERSED not in statuses
        assert constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL not in statuses


@pytest.mark.parametrize('reversed_permitted', (True, False))
async def test_reversed_status_permissions(
        cbox: conftest.CboxWrap, patch_auth, reversed_permitted: bool,
):
    groups = ['chatterbox_reversed_status'] if reversed_permitted else []
    patch_auth(superuser=False, groups=groups)

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert_reversed_status(cbox.body_data, reversed_permitted)

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'online', 'lines': ['first']},
    )
    assert cbox.status == 200
    assert_reversed_status(cbox.body_data, reversed_permitted)


def assert_in_additional_status(
        body: dict, in_additional_permitted: bool,
) -> None:
    statuses = {status['id'] for status in body['status_list']}
    if in_additional_permitted:
        assert constants.STATUS_ONLINE_IN_ADDITIONAL in statuses
        assert constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL in statuses
    else:
        assert constants.STATUS_ONLINE_IN_ADDITIONAL not in statuses
        assert constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL not in statuses


@pytest.mark.parametrize('in_additional_permitted', (True, False))
async def test_in_additional_status_permissions(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        in_additional_permitted: bool,
):
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.supporter_profile('
        'supporter_login, in_additional_permitted)'
        'VALUES (%s, %s)',
        ('superuser', in_additional_permitted),
    )

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'online', 'lines': ['first']},
    )
    assert cbox.status == 200
    assert_in_additional_status(cbox.body_data, in_additional_permitted)

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert_in_additional_status(cbox.body_data, in_additional_permitted)


async def test_current_status_always_in_status_list(
        cbox: conftest.CboxWrap, pgsql: Dict[str, control.PgDatabaseWrapper],
):
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters VALUES (%s, %s, %s, %s)',
        ('superuser', 'online', ['second'], True),
    )
    cursor.execute(
        'INSERT INTO chatterbox.supporter_profile('
        'supporter_login, in_additional_permitted)'
        'VALUES (%s, %s)',
        ('superuser', False),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    status_list = {status['id'] for status in cbox.body_data['status_list']}
    assert 'online-in-additional' in status_list


@pytest.mark.usefixtures('support_metrics_mock')
@pytest.mark.parametrize('is_limit_reached', (True, False))
async def test_incoming_calls_shift_limit(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        is_limit_reached: bool,
):
    @patch(
        'chatterbox.internal.tasks_manager.TasksManager.'
        'is_tasks_per_shift_limit_reached',
    )
    async def _is_tasks_per_shift_limit_reached(
            supporter_state, log_extra=None,
    ):
        return is_limit_reached

    patch_auth(superuser=False, groups=['incoming_calls_permitted'])
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', 'online', ['second'], False),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert cbox.body_data['incoming_calls_allowed'] is not is_limit_reached

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'online', 'lines': ['first']},
    )
    assert cbox.status == 200
    assert cbox.body_data['incoming_calls_allowed'] is not is_limit_reached

    assert _is_tasks_per_shift_limit_reached.calls


@pytest.mark.usefixtures('support_metrics_mock')
@pytest.mark.parametrize('in_additional_permitted', (True, False))
async def test_incoming_calls_in_additional(
        cbox: conftest.CboxWrap,
        patch_auth,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        in_additional_permitted: bool,
):
    patch_auth(superuser=False, groups=['incoming_calls_permitted'])
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', 'online', ['second'], True),
    )
    cursor.execute(
        'INSERT INTO chatterbox.supporter_profile('
        'supporter_login, in_additional_permitted)'
        'VALUES (%s, %s)',
        ('superuser', in_additional_permitted),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    assert cbox.body_data['incoming_calls_allowed'] is in_additional_permitted

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'online-in-additional', 'lines': ['first']},
    )
    if in_additional_permitted:
        assert cbox.status == 200
        assert (
            cbox.body_data['incoming_calls_allowed'] is in_additional_permitted
        )
    else:
        assert cbox.status == 403
        assert cbox.body_data == {
            'code': 'forbidden',
            'message': 'errors.compendium_status_change',
            'status': 'error',
        }
