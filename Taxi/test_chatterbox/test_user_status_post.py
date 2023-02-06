# pylint: disable=redefined-outer-name
import asyncio
import datetime
from typing import Dict
from typing import Optional
from typing import Union

import pytest

from taxi import discovery
from taxi.clients import support_metrics
from testsuite.databases.pgsql import control

from chatterbox import constants
from test_chatterbox import plugins as conftest


NOW = datetime.datetime(2019, 8, 13, 12, 0, 0)


def get_db_status(current_status: str) -> tuple:
    if current_status.endswith(constants.IN_ADDITIONAL):
        in_additional = True
        db_current_status = current_status.split(constants.IN_ADDITIONAL)[0]
    else:
        in_additional = False
        db_current_status = current_status
    return db_current_status, in_additional


@pytest.mark.config(
    CHATTERBOX_DASHBOARD_TIMEOUT_BY_LINE={
        '__default__': 5,
        'first': 10,
        'second': 3,
    },
)
@pytest.mark.parametrize(
    'db_user_params', (tuple(), ('online', ['second'], True)),
)
@pytest.mark.parametrize(
    ('request_params', 'expected_result'),
    (
        (
            {'current_status': 'offline', 'lines': []},
            {
                'current_status': 'offline',
                'lines': [],
                'dashboard_next_request_timeout': 5,
            },
        ),
        (
            {'current_status': 'offline', 'lines': ['first']},
            {
                'current_status': 'offline',
                'lines': ['first'],
                'dashboard_next_request_timeout': 10,
            },
        ),
        (
            {'current_status': 'online', 'lines': ['second']},
            {
                'current_status': 'online',
                'lines': ['second'],
                'dashboard_next_request_timeout': 3,
            },
        ),
        (
            {'current_status': 'online-in-additional', 'lines': ['first']},
            {
                'current_status': 'online-in-additional',
                'lines': ['first'],
                'dashboard_next_request_timeout': 10,
            },
        ),
        (
            {
                'current_status': 'online-in-additional',
                'lines': ['first', 'second'],
            },
            {
                'current_status': 'online-in-additional',
                'lines': ['first', 'second'],
                'dashboard_next_request_timeout': 3,
            },
        ),
    ),
)
async def test_change_status_params(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        request_params: dict,
        expected_result: dict,
        db_user_params: tuple,
        patch_aiohttp_session,
        response_mock,
):

    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['created'],
        )
        events = kwargs['json']['events']
        assert len(events) == 2
        for event in events:
            assert event['type'] == 'supporter_status'
            assert event['payload']['login'] == 'superuser'
            assert event['payload']['in_addition']
            assert event['payload']['status'] == 'online'
            assert event['payload']['lines'] == ['second']
            assert event['payload']['projects'] == ['taxi']
            finish_timestamp = event['payload']['finish_timestamp']
            start_timestamp = event['payload']['start_timestamp']
            assert finish_timestamp > start_timestamp
        return response_mock(json={})

    if db_user_params:
        cursor = pgsql['chatterbox'].cursor()
        cursor.execute(
            'INSERT INTO chatterbox.online_supporters('
            '   supporter_login, status, lines, in_additional, updated'
            ')'
            'VALUES (%s, %s, %s, %s, %s)',
            ('superuser', *db_user_params, NOW),
        )

    await cbox.post('/v1/user/status', data=request_params)
    assert cbox.status == 200
    body = cbox.body_data
    skip_check_fields = (
        'status_list',
        'incoming_calls_allowed',
        'default_work_status',
        'assigned_lines',
        'can_choose_from_assigned_lines',
        'can_choose_except_assigned_lines',
    )
    for field in skip_check_fields:
        body.pop(field)

    assert body == {
        'available_modes': ['offline', 'online'],
        'next_request_timeout': 60000,
        **expected_result,
    }


@pytest.mark.parametrize(
    'status', (None, 'offline', 'online', 'online-in-additional'),
)
async def test_change_status_validation(
        cbox: conftest.CboxWrap, status: Optional[str],
):
    request_data: Dict[str, Union[str, list]] = {}

    if status is not None:
        request_data['current_status'] = status

    await cbox.post('/v1/user/status', data=request_data)
    assert cbox.status == 400


@pytest.mark.parametrize('current_status', tuple(constants.SUPPORT_STATUSES))
async def test_change_user_status_available_change(
        cbox: conftest.CboxWrap, patch, current_status: str,
):
    @patch('chatterbox.api.user_utils.validate_status_change')
    async def _validate_status_change(*args, **kwargs):
        pass

    await cbox.post(
        '/v1/user/status',
        data={'current_status': current_status, 'lines': ['first']},
    )
    assert cbox.status == 200
    available_status = {
        status['id'] for status in cbox.body_data['status_list']
    }
    expected_status_list = {
        current_status,
        *constants.STATUSES_AVAILABLE_FOR_CHANGE[current_status],
    }
    assert available_status == expected_status_list


@pytest.mark.parametrize('current_status', tuple(constants.SUPPORT_STATUSES))
@pytest.mark.parametrize('new_status', tuple(constants.SUPPORT_STATUSES))
async def test_change_status_change_validation(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        current_status: str,
        new_status: str,
        support_metrics_mock,
):
    db_current_status, in_additional = get_db_status(current_status)

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', db_current_status, ['second'], in_additional),
    )

    available = constants.STATUSES_AVAILABLE_FOR_CHANGE[current_status]
    await cbox.post(
        '/v1/user/status',
        data={'current_status': new_status, 'lines': ['first']},
    )
    if new_status in available or new_status == current_status:
        assert cbox.status == 200
    else:
        assert cbox.status == 400
        assert cbox.body_data == {
            'code': 'bad_request',
            'message': 'Incorrect status change from {} to {}'.format(
                current_status, new_status,
            ),
            'status': 'error',
        }


@pytest.mark.config(CHATTERBOX_USE_ASSIGNED_LINES=True)
@pytest.mark.parametrize(
    ('login', 'input_data', 'status'),
    (
        ('user_1', {'lines': ['line_1', 'line_2']}, 200),
        ('user_1', {'lines': ['line_1']}, 400),
        ('user_2', {'lines': ['line_1']}, 400),
        ('user_3', {'lines': ['line_3']}, 400),
    ),
)
async def test_validate_user_lines(
        cbox, patch_auth, login, input_data, status,
):
    patch_auth(login=login)
    input_data['current_status'] = constants.STATUS_ONLINE
    await cbox.post('/v1/user/status', data=input_data)
    assert cbox.status == status


@pytest.mark.parametrize(
    ('login', 'input_data', 'current_status', 'response'),
    (
        ('user_1', {'lines': ['line_1', 'line_2']}, 'offline', 200),
        ('user_1', {'lines': ['line_1', 'line_2']}, 'technical_problems', 200),
    ),
)
async def test_check_clearing_offer_skip_count(
        cbox,
        patch_auth,
        patch_aiohttp_session,
        response_mock,
        login,
        input_data,
        current_status,
        response,
):
    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        return response_mock(json={})

    async with cbox.app.pg_master_pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO chatterbox.online_supporters VALUES ($1, $2, $3, $4)',
            login,
            'online',
            input_data['lines'],
            False,
        )

    patch_auth(login=login)
    input_data['current_status'] = current_status
    await cbox.post('/v1/user/status', data=input_data)
    assert cbox.status == response

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = $1',
            login,
        )
    assert result[0]['offer_skip_count'] == 0


@pytest.mark.parametrize('reversed_permitted', (True, False))
@pytest.mark.parametrize(
    'new_status',
    (
        constants.STATUS_ONLINE_REVERSED,
        constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL,
    ),
)
async def test_change_status_to_reversed_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        reversed_permitted: bool,
        new_status: str,
):
    groups = ['chatterbox_reversed_status'] if reversed_permitted else []
    patch_auth(superuser=False, groups=groups)

    await cbox.post(
        '/v1/user/status',
        data={'current_status': new_status, 'lines': ['first']},
    )
    if reversed_permitted:
        assert cbox.status == 200
    else:
        assert cbox.status == 403
        assert cbox.body_data == {
            'code': 'permission_forbidden',
            'message': 'Status require permissions',
            'status': 'error',
        }


async def test_change_status_to_offline_validation(
        cbox: conftest.CboxWrap,
        patch_auth,
        pgsql: Dict[str, control.PgDatabaseWrapper],
):
    patch_auth(login='user_with_task')

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', 'online', ['first'], False),
    )

    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'offline', 'lines': ['first']},
    )
    assert cbox.status == 400
    assert cbox.body_data == {
        'code': 'bad_request',
        'message': 'You can\'t go offline while tasks on you',
        'status': 'error',
    }


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_status_change': {
            'ru': 'Compendium заблокировал смену статуса в доп.',
        },
    },
)
@pytest.mark.parametrize(
    'new_status',
    (
        constants.STATUS_ONLINE_IN_ADDITIONAL,
        constants.STATUS_ONLINE_REVERSED_IN_ADDITIONAL,
    ),
)
async def test_change_status_compendium_validation(
        cbox: conftest.CboxWrap,
        new_status: str,
        pgsql: Dict[str, control.PgDatabaseWrapper],
):
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.supporter_profile('
        'supporter_login, in_additional_permitted)'
        'VALUES (%s, %s)',
        ('superuser', False),
    )

    await cbox.post(
        '/v1/user/status',
        data={'current_status': new_status, 'lines': ['first']},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 403
    assert cbox.body_data == {
        'code': 'forbidden',
        'message': 'Compendium заблокировал смену статуса в доп.',
        'status': 'error',
    }


async def test_change_status_timestamp(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        support_metrics_mock,
):

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', 'offline', [], False),
    )
    await cbox.post(
        '/v1/user/status',
        data={'current_status': 'online', 'lines': ['first']},
    )
    assert cbox.status == 200

    cursor.execute(
        'SELECT last_action_ts, updated FROM chatterbox.online_supporters '
        'WHERE supporter_login = %s',
        ('superuser',),
    )
    result = cursor.fetchone()
    last_action_ts = result[0]
    updated = result[1]

    assert last_action_ts
    assert updated


@pytest.mark.parametrize('error_code', (500, 400))
@pytest.mark.parametrize(
    ('db_user_params', 'request_params', 'expected_result'),
    [
        (
            ('online', ['second'], True),
            {'current_status': 'offline', 'lines': ['first']},
            {'current_status': 'offline', 'lines': ['first']},
        ),
    ],
)
async def test_send_events_error(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        db_user_params: tuple,
        request_params: dict,
        expected_result: dict,
        error_code: int,
        patch_aiohttp_session,
        response_mock,
):

    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        return response_mock(status=error_code)

    async def send_status_to_support_metrics(app, log_extra=None):
        if not app.config.CHATTERBOX_SEND_STATUS_EVENTS_ENABLED:
            return None
        return asyncio.create_task(
            app.support_metrics_client.send_events_bulk(
                None, log_extra=log_extra,
            ),
        )

    tasks = await send_status_to_support_metrics(cbox.app)

    with pytest.raises(support_metrics.BaseError):
        await tasks
