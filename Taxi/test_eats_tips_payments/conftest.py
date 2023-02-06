# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import http
import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as testsuite_http

from taxi.clients import tvm

import eats_tips_payments.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from eats_tips_payments.utils.plus import calculate as plus_calc

pytest_plugins = ['eats_tips_payments.generated.service.pytest_plugins']


TEST_UID = '42'


DEFAULT_PLUS_SETTINGS_CFG = {
    'enabled': True,
    'max_amount_per_transaction': plus_calc.PLUS_MAX_AMOUNT_FALLBACK,
}

# tvmknife unittest user -d 42
TEST_USER_TICKET = (
    '3:user:CA0Q__________9_Gg4KAggqECog0oXYzAQoAQ:JYF5_O7nRBnzdqYMCH37kr14L9o'
    'Vhr1Bchy8ziJ5EyqEt0ykJ-fp8M8DsrseMhA7UHlhBp8b6PauS0rTFajeLYDBcO0VOvTOozJc'
    'vSIQDLj8EdG7cUAFFWtMj72tDIoXU5_JNlSYgzmclNWbChFlcW5gRiYBz87Y6ptvRwptRU8'
)

# tvmknife unittest user -d 123
TEST_USER_TICKET_2 = (
    '3:user:CA0Q__________9_Gg4KAgh7EHsg0oXYzAQoAQ:AYh026vdpoBwpJfZGcNlDEs9lrr'
    'ohky2Ys9HcOHjNJ_fwVeiTdqlHnsAvhZfFmgzSbTh2sSyFv5d12CGbLF3LT-pPO0MYfcxTefC'
    'aZkJjtbkhzGA7e-Oxx9tqj61yy9Pojd0K2igvMYvuIhlS3Q_JtGjmeEVrADpEBbitFouYTc'
)

VALID_TVM_HEADER = {
    tvm.YANDEX_UID_HEADER: TEST_UID,
    tvm.TVM_USER_TICKET_HEADER: TEST_USER_TICKET,
}

ENABLED_PLUS_CONFIG = {
    'enabled': True,
    'max_amount_per_transaction': plus_calc.PLUS_MAX_AMOUNT_FALLBACK,
    'service_name': 'tips',
    'service_id': '142',
    'issuer': 'simple_services',
    'ticket': 'ABC-123',
}
INVOICE = {
    'id': 'order_id',
    'invoice_due': '2021-09-11T08:44:26+03:00',
    'currency': 'RUB',
    'status': 'init',
    'payment_types': [],
    'sum_to_pay': [],
    'held': [
        {
            'payment_type': 'card',
            'items': [{'item_id': 'ride', 'amount': '20'}],
        },
    ],
    'cleared': [],
    'debt': [],
    'operation_info': {},
    # Transactions aren't relevant to our particular use case,
    # but in reality they are not empty
    'transactions': [],
    'yandex_uid': 'yandex_uid_1',
    'operations': [],
    'cashback': {
        'status': 'init',
        'version': 1,
        'rewarded': [],
        'transactions': [],
        'operations': [],
        'commit_version': 1,
    },
    'user_ip': '2a02:6b8:b010:50a3::3',
}


def get_tvm_user_ticket_cases(ticket_required=False) -> typing.Tuple:
    """Return test cases for checking tvm user ticket.

    If ticket_required is True then expects BAD_REQUEST for missing
    X-Ya-User-Ticket header, otherwise expects OK.
    """
    if ticket_required:
        status_by_required = http.HTTPStatus.BAD_REQUEST
    else:
        status_by_required = http.HTTPStatus.OK
    return (
        (VALID_TVM_HEADER, http.HTTPStatus.OK),
        (
            {
                tvm.YANDEX_UID_HEADER: TEST_UID,
                tvm.TVM_USER_TICKET_HEADER: TEST_USER_TICKET_2,
            },
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            {tvm.YANDEX_UID_HEADER: TEST_UID, tvm.TVM_USER_TICKET_HEADER: ''},
            http.HTTPStatus.FORBIDDEN,
        ),
        ({tvm.YANDEX_UID_HEADER: TEST_UID}, status_by_required),
        ({tvm.TVM_USER_TICKET_HEADER: TEST_UID}, http.HTTPStatus.FORBIDDEN),
        (None, status_by_required),
    )


def make_stat(labels: dict) -> dict:
    return {'kind': 'IGAUGE', 'labels': labels, 'timestamp': None, 'value': 1}


@pytest.fixture
async def mock_process_cron(mock_chaevieprosto):
    def wrapper(query_type):
        @mock_chaevieprosto('/obrabotka-krona.html')
        async def _process_cron(request: testsuite_http.Request):
            assert request.headers.get('X-API-Key') == 'some_token'
            assert request.query.get('type') == query_type
            return web.Response(
                status=200, text='OK', content_type='text/html',
            )

    return wrapper


@pytest.fixture(name='transactions_mock')
def _transactions_mock(mock_transactions_ng, mockserver):
    @mock_transactions_ng('/v2/invoice/retrieve')
    def _mock_retrieve_invoice(request):
        return INVOICE

    @mock_transactions_ng('/v2/invoice/create')
    def _mock_create_invoice(request):
        return {}

    @mock_transactions_ng('/v2/cashback/update')
    def _mock_cashback_update(request):
        return {}


@pytest.fixture(name='mock_plus_balances')
def _mock_plus_balances(mock_plus_wallet):
    @mock_plus_wallet('/v1/balances')
    def _handler(request):
        return {
            'balances': [
                {'balance': '0', 'wallet_id': 'wallet_1', 'currency': 'RUB'},
            ],
        }

    return _handler


def check_task_queued(stq, queue, kwargs, drop=()):
    task = queue.next_call()
    assert task.pop('eta')
    assert task.pop('id')
    assert task.pop('queue')
    for arg in drop:
        task['kwargs'].pop(arg)
    assert task == {'args': [], 'kwargs': kwargs}


def check_task_rescheduled(stq, queue, eta):
    task = queue.next_call()
    assert task.pop('id')
    assert task.pop('queue')
    assert task == {
        'eta': eta.replace(tzinfo=None),
        'args': None,
        'kwargs': None,
    }
    assert stq.is_empty


PLACE_ID_1 = 'eef266b2-09b3-4218-8da9-c90928608d97'
PLACE_ID_2 = 'eef266b2-09b3-4218-8da9-c90928608d98'
PLACE_ID_3 = '00000000-0000-0000-0000-000000000021'
PLACE_ID_4 = '00000000-0000-0000-0000-000000000022'
PARTNER_ID_1 = 'f907a11d-e1aa-4b2e-8253-069c58801727'
PARTNER_ID_2 = 'f907a11d-e1aa-4b2e-8253-069c58801722'
PARTNER_ID_3 = '00000000-0000-0000-0000-000000000030'
PARTNER_ID_4 = '00000000-0000-0000-0000-000000000040'
PARTNER_ID_17 = '00000000-0000-0000-0000-000000000170'
NOT_FOUND_ID = '00000000-0000-0000-0000-000000000000'


@pytest.fixture
async def mock_eats_tips_partners_for_settings(mock_eats_tips_partners):
    @mock_eats_tips_partners('/v1/partner')
    def mock_v1_partner(request: testsuite_http.Request):
        partner_id = request.query['partner_id']
        mysql_ids_by_partner_id = {PARTNER_ID_1: '1'}
        return web.json_response(
            {
                'id': partner_id,
                'b2p_id': 'partner_b2p_id_1',
                'display_name': '',
                'full_name': '',
                'phone_id': 'phone_id_1',
                'saving_up_for': '',
                'best2pay_blocked': False,
                'registration_date': '1970-01-01T03:00:00+03:00',
                'is_vip': False,
                'blocked': False,
                'mysql_id': mysql_ids_by_partner_id.get(partner_id),
            },
            status=200,
        )

    @mock_eats_tips_partners('/v1/place')
    def mock_v1_place(request: testsuite_http.Request):
        place_id = request.query['place_id']
        mysql_ids_by_place_id = {
            PLACE_ID_1: '3',
            PLACE_ID_2: '4',
            PLACE_ID_3: '21',
            PLACE_ID_4: '22',
        }
        brand_slugs_by_place_id = {PLACE_ID_1: 'shoko', PLACE_ID_4: 'shoko'}
        result = {
            'id': request.query['place_id'],
            'title': '',
            'alias': '',
            'photo': '',
            'mysql_id': mysql_ids_by_place_id.get(place_id),
            'brand_slug': brand_slugs_by_place_id.get(place_id),
        }
        return web.json_response(
            dict(filter(lambda item: item[1] is not None, result.items())),
            status=200,
        )


class _Sentinel:
    pass


SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value


@pytest.fixture
def insert_row(pgsql):
    def _create(table: str, row: dict, ret: str = 'id') -> str:
        with pgsql['eats_tips_payments'].cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO eats_tips_payments.{table}
                ({", ".join(row.keys())})
                VALUES ({", ".join(["%s"] * len(row))})
                RETURNING {ret}
                """,
                list(row.values()),
            )
            return cursor.fetchone()[0]

    return _create
