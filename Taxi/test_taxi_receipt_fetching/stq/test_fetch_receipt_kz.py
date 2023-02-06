import dataclasses

import pytest

from taxi_receipt_fetching.common import http_client
from taxi_receipt_fetching.stq import task


@dataclasses.dataclass
class CallsMocks:
    def __init__(
            self,
            test_settings,
            client_session_request_mock,
            archive_mock,
            order_proc_retrieve_mock,
            br_person_mock,
            br_contracts_mock,
            load_json,
    ):
        self.client_session_mock = client_session_request_mock(
            resp_data=test_settings['receipt_client_response'],
            status=test_settings['receipt_client_response']['status_code'],
        )
        self.archive_proc_mock = order_proc_retrieve_mock(
            load_json(test_settings['order_proc']),
        )
        self.archive_order_mock = archive_mock(
            load_json(test_settings['order']), 'get_order_by_id',
        )
        self.person_mock = br_person_mock(
            load_json(test_settings['billing_replication_person']),
        )
        self.contract_mock = br_contracts_mock(
            load_json(test_settings['billing_replication_contract']), [],
        )


@pytest.mark.parametrize(
    'test_json',
    [
        'cash_order_success.json',
        'cash_order_invalid_data.json',
        'cash_order_partner_not_found.json',
        'cash_order_partner_kassa_not_found.json',
        'cash_order_already_registered.json',
        'card_order_success.json',
        'card_order_billing_response_error.json',
        'card_order_old_due.json',
        'cash_order_tariff_express.json',
        'cash_order_no_cost.json',
        'card_order_no_clear_time.json',
        'card_order_no_clear_amount.json',
        'card_order_rest_api_clear_fields.json',
        'card_order_rest_api_unhold.json',
        'card_order_with_cashback.json',
        'card_order_with_cashback_reversal.json',
        'card_order_cargo_success.json',
    ],
)
@pytest.mark.config(
    RECEIPT_CLIENT_SETTINGS={
        '__default__': {
            'base_url': None,
            'base_receipt_url': None,
            'timeout': 0.5,
            'retries': 2,
            'enabled': False,
        },
        'buhta': {
            'base_url': 'https://buhta.kz/api/v1/kassa/yt',
            'base_receipt_url': 'https://buhta.kz/yt',
            'timeout': 0.5,
            'retries': 2,
            'enabled': True,
        },
    },
    RECEIPT_REGISTRATION_ENABLED={'__default__': True},
    TRANSACTIONS_RECEIPT_HANDLING_ENABLED={'__default__': True},
    PAYMENT_SERVICES_SETTINGS={
        '__default__': {'__default__': []},
        'kaz': {
            '__default__': [],
            'card': [124, 125],
            'cash': [111],
            'cargo_card': [1162],
        },
    },
    FISCAL_TITLE_TARIFF_CLASSES=['express'],
    RECEIPT_KAZAKHSTAN_CASHBACK_PARK_SETTINGS={
        'client_id': '12345601',
        'services': [111],
    },
    RECEIPT_KAZAKHSTAN_CASHBACK_PROCESSING_ENABLED=True,
)
@pytest.mark.filldb(parks='test_kz', tariff_settings='test_kz')
@pytest.mark.translations(
    client_messages={
        'fiscal_receipt.title.rus': {'ru': 'Перевозка пассажиров и багажа'},
        'fiscal_receipt.title.rus.express': {
            'ru': 'Услуги курьерской доставки',
        },
        'fiscal_receipt.cashback.title': {
            'ru': 'Расширенный уровень подписки Яндекс.Плюс',
        },
    },
)
async def test_fetch_receipt(
        stq3_context,
        fetch_receipt_task_info,
        load_json,
        archive_mock,
        order_proc_retrieve_mock,
        br_person_mock,
        br_contracts_mock,
        client_session_request_mock,
        test_json,
):
    test_settings = load_json(test_json)
    order_id = test_settings['order_id']

    await _check_receipt_rows(stq3_context, order_id, expected_rows=[])

    await _load_existing_payment_ids(
        stq3_context, order_id, test_settings['existing_payment_ids'],
    )

    calls_mocks = CallsMocks(
        test_settings,
        client_session_request_mock,
        archive_mock,
        order_proc_retrieve_mock,
        br_person_mock,
        br_contracts_mock,
        load_json,
    )

    expected_exception = test_settings['expected_exception']

    if expected_exception:
        with pytest.raises(Exception) as exc:
            await task.fetch_receipt(
                stq3_context, fetch_receipt_task_info, order_id,
            )
            assert isinstance(exc, expected_exception)
            _check_calls_and_client_request(test_settings, calls_mocks)
    else:
        await task.fetch_receipt(
            stq3_context, fetch_receipt_task_info, order_id,
        )
        _check_calls_and_client_request(test_settings, calls_mocks)

        await _check_receipt_rows(
            stq3_context,
            order_id,
            expected_rows=test_settings['expected_receipt_rows'],
        )
        await _check_payment_id_registration(
            stq3_context,
            order_id,
            expected_rows=test_settings['expected_payment_id_rows'],
        )


def _check_calls_and_client_request(test_settings, calls_mocks):
    expected_calls = test_settings['expected_calls']

    assert (
        len(calls_mocks.archive_proc_mock.calls)
        == expected_calls['archive_proc']
    )
    assert (
        len(calls_mocks.archive_order_mock.calls)
        == expected_calls['archive_order']
    )
    assert (
        len(calls_mocks.person_mock.calls)
        == expected_calls['billing_replication_person']
    )
    assert (
        len(calls_mocks.contract_mock.calls)
        == expected_calls['billing_replication_contract']
    )

    client_calls = calls_mocks.client_session_mock.calls
    assert len(client_calls) == expected_calls['client_session']
    for call, expected_call in zip(
            client_calls, test_settings['expected_receipt_client_requests'],
    ):
        assert call['kwargs']['json'] == expected_call


async def _load_existing_payment_ids(
        stq3_context, order_id, existing_payment_ids,
):
    postgres = stq3_context.postgresql.receipt_fetching[0]
    for existing_payment_id in existing_payment_ids:
        payment_id_query = stq3_context.postgres_queries[
            'create_receipt_by_payment_id.sql'
        ]
        payment_id_query_args = (
            existing_payment_id,
            order_id,
            'existing_payment_id_url',
        )
        await postgres.execute(payment_id_query, *payment_id_query_args)


async def _check_receipt_rows(stq3_context, order_id, expected_rows):
    query = stq3_context.postgres_queries['read_receipt.sql']
    args = ([order_id],)
    postgres = stq3_context.postgresql.receipt_fetching[0]
    rows = await postgres.primary_fetch(query, *args)
    rows = [
        {'order_id': row['order_id'], 'receipt_url': row['receipt_url']}
        for row in rows
    ]
    assert rows == expected_rows


async def _check_payment_id_registration(
        stq3_context, order_id, expected_rows,
):
    query_payment_id = stq3_context.postgres_queries[
        'read_payment_id_receipts.sql'
    ]
    postgres = stq3_context.postgresql.receipt_fetching[0]
    _args = ([order_id],)
    payment_id_rows = await postgres.primary_fetch(query_payment_id, *_args)
    rows = sorted(
        [
            {
                'order_id': row['order_id'],
                'payment_id': row['payment_id'],
                'receipt_url': row['receipt_url'],
            }
            for row in payment_id_rows
        ],
        key=_by_payment_id,
    )
    expected_rows = sorted(expected_rows, key=_by_payment_id)
    assert rows == expected_rows


@pytest.mark.config(
    RECEIPT_CLIENT_SETTINGS={
        '__default__': {},
        'buhta': {
            'base_url': 'https://buhta.kz/api/v1/kassa/yt',
            'base_receipt_url': 'https://buhta.kz/yt',
            'timeout': 0.5,
            'retries': 0,
            'enabled': True,
        },
    },
    RECEIPT_REGISTRATION_ENABLED={'__default__': True},
    PAYMENT_SERVICES_SETTINGS={'__default__': {'__default__': [111]}},
    FISCAL_TITLE_TARIFF_CLASSES=['express'],
)
@pytest.mark.filldb(parks='test_kz', tariff_settings='test_kz')
@pytest.mark.translations(
    client_messages={
        'fiscal_receipt.title.rus': {'ru': 'Перевозка пассажиров и багажа'},
    },
)
async def test_retries_exceeded(
        stq3_context,
        fetch_receipt_task_info,
        load_json,
        archive_mock,
        order_archive_mock,
        br_person_mock,
        br_contracts_mock,
):
    order_id = '97d56d68510e5f68a996b0b1f6815401'

    order_archive_mock.set_order_proc(load_json('order_proc.json'))
    archive_mock(load_json('orders.json'), 'get_order_by_id')
    br_person_mock(load_json('billing_replication_person.json'))
    br_contracts_mock(load_json('billing_replication_contract.json'), [])

    with pytest.raises(http_client.HttpClientRequestRetriesExceeded):
        await task.fetch_receipt(
            stq3_context, fetch_receipt_task_info, order_id,
        )


def _by_payment_id(row):
    return (row['order_id'], row['payment_id'])
