# pylint: disable=redefined-outer-name

import datetime
import hashlib
import json

import pytest

from taxi.clients import integration_api

NOW = datetime.datetime(2020, 9, 10, 9, 18, 40)
SBER_CLIENTS_SETTINGS = {
    'ввб нгосб/транспорт': {
        'client_id': 'client1',
        'class': 'econom',
        'timezone': 'Asia/Novosibirsk',
    },
}


def make_new_request(
        external_id: str = 'SD100039314', date: str = '13.09.2020 18:40:00',
):
    return {
        'СБ_ID': external_id,
        'ИНИЦИАТОР': 'Сергей Николаевич',
        'РГ': 'ввб нгосб/транспорт',
        'ИНФОРМАЦИЯ': f"""
        Время и Дата выезда: {date}
        Мобильный телефон: 7 111 111 11 11
        Адрес пункта отправления: Москва, улица Вавилова, 19
        Адрес пункта назначения: Москва, Кутузовский проспект, 32
        Адрес пункта назначения: Москва, 2-й Южнопортовый проезд
        Адрес пункта назначения: Москва, улица Вавилова, 19
        Комментарий водителю: тест
        """,
    }


def make_expected_claim(**kwargs):
    claim = {
        'external_id': 'SD100039314',
        'status': None,
        'close_status': None,
        'error_reason': None,
        'personal_phone_id': 'defee2e75b2039c74d9cfbc068d0aef7',
        'route': (
            '['
            '"Москва, улица Вавилова, 19", '
            '"Москва, Кутузовский проспект, 32", '
            '"Москва, 2-й Южнопортовый проезд", '
            '"Москва, улица Вавилова, 19"'
            ']'
        ),
        'taxi_order_id': None,
    }
    claim.update(**kwargs)
    return claim


def make_in_progress_response(**kwargs):
    response = {
        'ID': '1',
        'СБ_ID': 'SD100039314',
        'ИДЕНТИФИКАТОР': 'order_id_cabinet_api',
        'СТАТУС': '1',
        'ВРЕМЯ_ОБНОВЛЕНИЯ_МЕСТОПОЛОЖЕНИЯ': '2020-09-10 12:18:40',
        'ТЕКУЩЕЕ_МЕСТОПОЛОЖЕНИЕ': '2:1',
    }
    response.update(**kwargs)
    return {'IN_PROGRESS': response}


@pytest.fixture
def mock_yamaps(mockserver, load_json):
    @mockserver.json_handler('/yamaps/yandsearch')
    async def _yandsearch(request):
        return load_json('yamaps_response.json')


@pytest.fixture
def mock_corp_cabinet(mockserver):
    class Context:
        def __init__(self):
            self.draft_internal_error = False
            self.processing_internal_error = False
            self.zone_available = True
            self.processing_order_not_found = False

    context = Context()

    @mockserver.json_handler(
        r'/corp-cabinet/internal/1.0/client/(?P<client_id>\w+)/order',
        regex=True,
    )
    async def _create_draft(request, client_id):
        if context.draft_internal_error:
            return mockserver.make_response('internal error', status=500)

        if not context.zone_available:
            return mockserver.make_response(
                json.dumps(
                    {
                        'message': 'Zone not available',
                        'errors': [],
                        'code': '406',
                    },
                ),
                status=406,
            )

        return mockserver.make_response(
            json.dumps({'_id': 'order_id_cabinet_api'}), status=200,
        )

    @mockserver.json_handler(
        r'/corp-cabinet/internal/1.0/order/(?P<order_id>\w+)/processing',
        regex=True,
    )
    async def _processing(request, order_id):
        if context.processing_internal_error:
            return mockserver.make_response('internal error', status=500)

        if context.processing_order_not_found:
            return mockserver.make_response(
                json.dumps(
                    {
                        'message': 'Order not found',
                        'errors': [],
                        'code': '404',
                    },
                ),
                status=404,
            )

        return mockserver.make_response(
            json.dumps({'_id': order_id, 'status': {'full': 'scheduled'}}),
            status=200,
        )

    return context


@pytest.fixture
def mock_integration_api(patch):
    @patch(
        'client_integration_api.components.IntegrationAPIClient.order_search',
    )
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200,
            data={'orders': [{'vehicle': {'location': [1, 2]}}]},
            headers={},
        )


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _phones_store(request):
        value = request.json['value']
        return {'value': value, 'id': hashlib.md5(value.encode()).hexdigest()}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('sber_int_api', files=('claims.sql',))
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'sber-int-api'}])
@pytest.mark.parametrize(
    'order_proc, new_request, expected_response, expected_claim',
    [
        pytest.param(
            {'_id': 'order_id_cabinet_api'},
            make_new_request(date='08.09.2020 18:40:00'),
            {
                'DONE': {
                    'ID': '1',
                    'СБ_ID': 'SD100039314',
                    'СТАТУС': '9',
                    'КОД_ЗАКРЫТИЯ': '3',
                    'РЕШЕНИЕ': 'дата выезда устарела',
                },
            },
            make_expected_claim(
                status='new',
                close_status='failed',
                error_reason='дата выезда устарела',
                taxi_order_id=None,
            ),
            id='new_claim_old_date',
        ),
        pytest.param(
            {'_id': 'order_id_cabinet_api'},
            make_new_request(),
            make_in_progress_response(),
            make_expected_claim(
                status='pending', taxi_order_id='order_id_cabinet_api',
            ),
            id='new_claim_now_date',
        ),
        pytest.param(
            {'_id': 'order_id_cabinet_api'},
            make_new_request(external_id='new'),
            make_in_progress_response(
                **{'СБ_ID': 'new', 'ИДЕНТИФИКАТОР': 'order_id_cabinet_api'},
            ),
            make_expected_claim(
                external_id='new',
                status='pending',
                taxi_order_id='order_id_cabinet_api',
            ),
            id='existing_claim_status_new',
        ),
        pytest.param(
            {'_id': 'order_id_cabinet_api'},
            make_new_request(external_id='draft'),
            make_in_progress_response(
                **{'СБ_ID': 'draft', 'ИДЕНТИФИКАТОР': 'order_id_cabinet_api'},
            ),
            make_expected_claim(
                external_id='draft',
                status='pending',
                taxi_order_id='order_id_cabinet_api',
            ),
            id='existing_claim_status_draft',
        ),
        pytest.param(
            {'_id': 'order_id_3'},
            make_new_request(external_id='pending'),
            make_in_progress_response(
                **{'СБ_ID': 'pending', 'ИДЕНТИФИКАТОР': 'order_id_3'},
            ),
            make_expected_claim(
                external_id='pending',
                status='pending',
                taxi_order_id='order_id_3',
            ),
            id='existing_claim_status_pending',
        ),
        pytest.param(
            {
                '_id': 'order_id_4',
                'created': None,
                'order': {'status': 'completed'},
            },
            make_new_request(external_id='complete'),
            {
                'DONE': {
                    'ID': '1',
                    'ВЫПОЛНЕНО': '2020-09-10 12:18:40',
                    'ЗАРЕГИСТРИРОВАНО': '2020-09-10 12:18:40',
                    'ИДЕНТИФИКАТОР': 'order_id_4',
                    'КОД_ЗАКРЫТИЯ': '1',
                    'НАЧАЛО РАБОТ': '2020-09-10 12:18:40',
                    'РЕШЕНИЕ': None,
                    'СБ_ID': 'complete',
                    'СТАТУС': '7',
                },
            },
            make_expected_claim(
                external_id='complete',
                status='complete',
                close_status='complete',
                taxi_order_id='order_id_4',
            ),
            id='existing_claim_status_complete',
        ),
    ],
)
async def test_new_handler(
        order_archive_mock,
        mock_yamaps,
        mock_personal,
        mock_integration_api,
        mock_corp_cabinet,
        cron_context,
        handler,
        new_request,
        expected_response,
        expected_claim,
        order_proc,
):
    order_archive_mock.set_order_proc(order_proc)

    response = await handler('NEW', new_request)
    assert response == expected_response

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'],
            new_request['СБ_ID'],
        )
    new_claim = dict(new_claim)
    assert new_claim == expected_claim


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_new_handler_create_draft_406(
        mock_yamaps, mock_corp_cabinet, cron_context, handler,
):
    mock_corp_cabinet.zone_available = False

    request = make_new_request()
    response = await handler('NEW', request)
    assert response == {
        'DONE': {
            'ID': '1',
            'СБ_ID': 'SD100039314',
            'СТАТУС': '9',
            'КОД_ЗАКРЫТИЯ': '3',
            'РЕШЕНИЕ': 'Zone not available',
        },
    }

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'],
            request['СБ_ID'],
        )
    new_claim = dict(new_claim)
    assert new_claim == make_expected_claim(
        status='new',
        close_status='failed',
        error_reason='Zone not available',
        taxi_order_id=None,
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_new_handler_order_process_404(
        mock_yamaps, mock_corp_cabinet, cron_context, handler,
):
    mock_corp_cabinet.processing_order_not_found = True

    request = make_new_request()
    response = await handler('NEW', request)
    assert response == {
        'DONE': {
            'ID': '1',
            'СБ_ID': 'SD100039314',
            'СТАТУС': '9',
            'КОД_ЗАКРЫТИЯ': '3',
            'РЕШЕНИЕ': 'Order not found',
        },
    }

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'],
            request['СБ_ID'],
        )
    new_claim = dict(new_claim)
    assert new_claim == make_expected_claim(
        status='draft',
        close_status='failed',
        error_reason='Order not found',
        taxi_order_id='order_id_cabinet_api',
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_new_handler_create_draft_500(
        mock_yamaps, mock_corp_cabinet, cron_context, handler,
):
    mock_corp_cabinet.draft_internal_error = True

    request = make_new_request()
    response = await handler('NEW', request)
    assert response == {}

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'],
            request['СБ_ID'],
        )
    new_claim = dict(new_claim)
    assert new_claim == make_expected_claim(
        status='new', close_status=None, error_reason=None, taxi_order_id=None,
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_new_handler_order_processing_500(
        mock_yamaps, mock_corp_cabinet, cron_context, handler,
):
    mock_corp_cabinet.processing_internal_error = True

    request = make_new_request()
    response = await handler('NEW', request)
    assert response == {}

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'],
            request['СБ_ID'],
        )
    new_claim = dict(new_claim)
    assert new_claim == make_expected_claim(
        status='draft',
        close_status=None,
        error_reason=None,
        taxi_order_id='order_id_cabinet_api',
    )
