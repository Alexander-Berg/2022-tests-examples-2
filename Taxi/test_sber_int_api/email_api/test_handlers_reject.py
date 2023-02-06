# pylint: disable=redefined-outer-name

import datetime
import json

import pytest

from taxi.clients import integration_api

NOW = datetime.datetime(2020, 9, 10, 9, 18, 40)
SBER_CLIENTS_SETTINGS = {
    'ввб нгосб/транспорт': {'client_id': 'client1', 'class': 'econom'},
}

REJECT_REQUEST = {'СБ_ID': 'e1', 'ИДЕНТИФИКАТОР': 'order_id_1'}


def make_reject_response(**kwargs):
    response = {
        'ID': '1',
        'ВЫПОЛНЕНО': '2020-09-10 12:18:40',
        'ЗАРЕГИСТРИРОВАНО': '2020-09-10 12:18:40',
        'ИДЕНТИФИКАТОР': 'order_id_1',
        'КОД_ЗАКРЫТИЯ': '4',
        'НАЧАЛО РАБОТ': '2020-09-10 12:18:40',
        'РЕШЕНИЕ': None,
        'СБ_ID': 'e1',
        'СТАТУС': '8',
    }
    response.update(**kwargs)
    return {'DONE': response}


def make_expected_claim(**kwargs):
    claim = {
        'external_id': 'e1',
        'status': 'user_canceled',
        'close_status': 'user_canceled',
        'taxi_order_id': 'order_id_1',
        'personal_phone_id': 'defee2e75b2039c74d9cfbc068d0aef7',
        'route': (
            '['
            '"Москва, улица Вавилова, 19", '
            '"Москва, Кутузовский проспект, 32"'
            ']'
        ),
        'error_reason': None,
    }
    claim.update(**kwargs)
    return claim


ORDER_PROC = {
    '_id': 'order_id_1',
    'order': {'status': 'cancelled', 'taxi_status': 'cancelled', 'cost': None},
    'created': NOW,
}


@pytest.fixture
def mock_corp_cabinet(mockserver):
    class Context:
        def __init__(self):
            self.free_cancel_allowed = True
            self.paid_cancel_allowed = True
            self.already_cancelled = False

    context = Context()

    @mockserver.json_handler(
        r'/corp-cabinet/internal/1.0/order/(?P<order_id>\w+)/cancel',
        regex=True,
    )
    async def _cancel(request, order_id):
        if context.already_cancelled:
            return mockserver.make_response(
                json.dumps(
                    {
                        'message': 'Order already cancelled',
                        'errors': [],
                        'code': '404',
                    },
                ),
                status=404,
            )

        if request.json['state'] == 'free' and not context.free_cancel_allowed:
            return mockserver.make_response(
                json.dumps(
                    {
                        'message': 'Free cancel not allowed',
                        'errors': [],
                        'code': '409',
                    },
                ),
                status=409,
            )

        if request.json['state'] == 'paid' and not context.paid_cancel_allowed:
            return mockserver.make_response(
                json.dumps(
                    {
                        'message': 'Paid cancel not allowed',
                        'errors': [],
                        'code': '409',
                    },
                ),
                status=409,
            )

        return mockserver.make_response(
            json.dumps({'_id': order_id}), status=200,
        )

    return context


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('sber_int_api', files=('claims.sql',))
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
@pytest.mark.parametrize(
    [
        'already_cancelled',
        'free_cancel_allowed',
        'paid_cancel_allowed',
        'expected_claim',
        'expected_response',
        'order_proc',
    ],
    [
        pytest.param(
            True,
            False,
            False,
            make_expected_claim(),
            make_reject_response(),
            ORDER_PROC,
            id='already_cancelled',
        ),
        pytest.param(
            False,
            True,
            False,
            make_expected_claim(),
            make_reject_response(),
            ORDER_PROC,
            id='cancel_free',
        ),
        pytest.param(
            False,
            False,
            True,
            make_expected_claim(),
            make_reject_response(),
            ORDER_PROC,
            id='cancel_paid',
        ),
        pytest.param(
            False,
            False,
            False,
            make_expected_claim(
                status='transporting', close_status='complete',
            ),
            make_reject_response(**{'КОД_ЗАКРЫТИЯ': '1', 'СТАТУС': '6'}),
            {
                '_id': 'order_id_1',
                'order': {
                    'status': 'assigned',
                    'taxi_status': 'transporting',
                    'cost': None,
                },
                'created': NOW,
            },
            id='cancel_not_allowed',
        ),
    ],
)
async def test_reject_handler(
        patch,
        cron_context,
        order_archive_mock,
        mock_corp_cabinet,
        handler,
        already_cancelled,
        free_cancel_allowed,
        paid_cancel_allowed,
        expected_claim,
        expected_response,
        order_proc,
):
    mock_corp_cabinet.already_cancelled = already_cancelled
    mock_corp_cabinet.free_cancel_allowed = free_cancel_allowed
    mock_corp_cabinet.paid_cancel_allowed = paid_cancel_allowed

    @patch(
        'client_integration_api.components.IntegrationAPIClient.order_search',
    )
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200,
            data={'orders': [{'vehicle': {'location': [1, 2]}}]},
            headers={},
        )

    order_archive_mock.set_order_proc(order_proc)

    response = await handler('REJECT', REJECT_REQUEST)
    assert response == expected_response

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'], 'e1',
        )
    new_claim = dict(new_claim)
    assert new_claim == expected_claim


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('sber_int_api', files=('claims.sql',))
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_reject_order_archive_500(order_archive_mock, handler):
    order_archive_mock.set_order_proc_retrieve_500()

    response = await handler('REJECT', REJECT_REQUEST)
    assert response == {}
