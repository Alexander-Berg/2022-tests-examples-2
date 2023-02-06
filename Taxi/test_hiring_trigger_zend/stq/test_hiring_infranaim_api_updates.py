from aiohttp import web
import pytest

from hiring_trigger_zend.stq import hiring_infranaim_api_updates
from test_hiring_trigger_zend import conftest


@conftest.configuration
@pytest.mark.parametrize(
    'ticket_data, is_valid, endpoint,'
    'can_use_hiring_api, use_hiring_api,'
    'call_hiring_api, call_infranaim_api',
    [
        ('valid_infranaim', True, None, False, False, False, True),
        ('valid_infranaim', True, None, False, True, False, True),
        ('valid_infranaim', True, None, True, False, False, True),
        ('valid_hiring_api', True, None, True, True, True, False),
        ('valid_infranaim', True, 'some', False, False, False, True),
        ('valid_infranaim', True, 'some', False, True, False, True),
        ('valid_infranaim', True, 'some', True, False, False, True),
        ('valid_hiring_api', True, 'some', True, True, True, False),
        ('invalid_id', False, None, False, False, False, False),
        ('invalid_id', False, None, False, True, False, False),
        ('invalid_id', False, None, True, False, False, False),
        ('invalid_id', False, None, True, True, False, False),
    ],
)
async def test_updates(
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_hiring_api,
        mock_infranaim_api,
        ticket_data,
        is_valid,
        endpoint,
        can_use_hiring_api,
        use_hiring_api,
        call_hiring_api,
        call_infranaim_api,
        taxi_config,
):
    @mock_hiring_api('/v1/tickets/update')
    async def update_mock(request, response_code=200):  # pylint: disable=W0612
        return web.json_response(
            {'code': str(response_code), 'message': ''}, status=response_code,
        )

    @mock_infranaim_api('/api/v1/update/all_tickets')
    async def all_tickets(request, response_code=200):
        if request.headers['token'] != 'TOKEN_ALL_TICKETS':
            raise ValueError(request.headers['token'])

    @mock_infranaim_api('/api/v1/update/some')
    async def some(request, response_code=200):
        if request.headers['token'] != 'TOKEN_SOME':
            raise ValueError(request.headers['token'])
        return web.json_response(
            {'code': response_code, 'message': '', 'details': ''},
        )

    stq3_context.config.HIRING_TRIGGER_ZEND_ENABLE_HIRING_API = use_hiring_api

    await hiring_infranaim_api_updates.task(
        stq3_context,
        task_id='1',
        **{
            'ticket_data': load_json('ticket_data.json')[ticket_data],
            'endpoint': endpoint,
            'can_use_hiring_api': can_use_hiring_api,
        },
    )

    if call_hiring_api:
        assert not all_tickets.has_calls
        assert not some.has_calls
        assert update_mock.has_calls
    else:
        assert not update_mock.has_calls

    if call_infranaim_api:
        if endpoint is None:
            assert all_tickets.has_calls
            assert not some.has_calls
        else:
            assert not all_tickets.has_calls
            assert some.has_calls
    else:
        assert not all_tickets.has_calls
        assert not some.has_calls


@conftest.configuration
@pytest.mark.parametrize(
    'params', ['duplicated', 'not_found', 'not_found_endpoint'],
)
async def test_update_40x(
        load_json, stq_runner, mock_infranaim_api, stq, params,
):
    params = load_json('params_update_40x.json')[params]

    @mock_infranaim_api('/api/v1/update/all_tickets')
    async def all_tickets(_):
        return web.json_response(
            status=params['status'], data=params['infranaim_response'],
        )

    await stq_runner.hiring_infranaim_api_updates.call(
        task_id='1',
        args='1',
        kwargs={
            'ticket_data': load_json('ticket_data.json')['valid_infranaim'],
            'endpoint': 'all_tickets',
        },
    )

    assert all_tickets.has_calls
    assert stq.hiring_infranaim_api_updates.times_called == params['stq_calls']
