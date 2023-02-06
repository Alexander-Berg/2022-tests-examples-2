import datetime

import pytest
import pytz


from tests_cashbox_integration import utils


CREDENTIAL = (
    'pymAmaIpQv+4Iwex1+Mi4QCaLTDJoJyuSZ/gXinbPd6zmlH7g3OKxIXp3a'
    'x2rcWxsB8ww/9fT1hKUwwl27wwMolQxL2CtCLFwX/L6O9i4DgLqW7iz202'
    'Ggsp5AvcDLiBl3ZK3a6q6qKMh2i6i368ciWQJglIiynrVYVT4X6FHMldmW'
    'XtLbUOz2OtewMKb+tDWycF/jJqqFDJDfHYLQR3LRfLh5wzDTpS/+Mj/f21'
    'wF4DPO8N8PGjQcJZa+Fj/YitNLiCRQqJQLcT7N5Pv8EsS6RhM272W2qf/A'
    'G/r70f15GQNjxGBucQYhOxEYO1AaWcF7nHp/w9ddu6cw2eRhtugQ=='
)


def enable_periodic_task(taxi_config):
    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )


def initialize():
    return (
        'park_id_1',
        'order_id_1',
        datetime.datetime.now(pytz.timezone('Europe/Moscow')),
        'uuid_1',
    )


def create_expected_receipt(status, task_uuid, fail_message, failure_id):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'
    external_id = 'uuid_1'
    order_price = 250.00
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00')

    return utils.create_receipt(
        park_id=park_id,
        driver_id=driver_id,
        order_id=order_id,
        cashbox_id=cashbox_id,
        external_id=external_id,
        status=status,
        order_price=order_price,
        order_end=order_end,
        task_uuid=task_uuid,
        fail_message=fail_message,
        failure_id=failure_id,
    )


def check_request_push(request):
    assert request['request'].method == 'POST'
    assert request['request'].headers['X-Signature'] == CREDENTIAL


async def test_add_task(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/documents')
    def od_post_receipt(request):
        return mockserver.make_response(status=201)

    park_id, order_id, updated_at, task_uuid = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_post_receipt.times_called >= 1
    check_request_push(od_post_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        task_uuid=task_uuid,
        fail_message=None,
        failure_id=None,
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at


async def test_inn_not_found(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/documents')
    def od_post_receipt(request):
        return mockserver.make_response(
            json={'errors': ['организация не найдена']}, status=400,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_post_receipt.times_called >= 1
    check_request_push(od_post_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message='Orange Data bad request: организация не найдена',
        failure_id='kUnknownInn',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_signature_failed(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/documents')
    def od_post_receipt(request):
        return mockserver.make_response(
            json={'errors': ['Подпись не прошла проверку']}, status=400,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_post_receipt.times_called >= 1
    check_request_push(od_post_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message='Orange Data bad request: Подпись не прошла проверку',
        failure_id='kSignatureFailed',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_queue_overflow(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/documents')
    def od_post_receipt(request):
        return mockserver.make_response(
            json={'errors': ['Очередь переполнена']}, status=503,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_post_receipt.times_called >= 1
    check_request_push(od_post_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=(
            'Orange Data queue is too long: POST /api/v2/documents, '
            + 'status code 503'
        ),
        failure_id='kQueueOverflow',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_wrong_credentials(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/documents')
    def od_post_receipt(request):
        return mockserver.make_response(
            json={'errors': ['Клиентский сертификат не прошел проверку']},
            status=401,
        )

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_post_receipt.times_called >= 1
    check_request_push(od_post_receipt.next_call())

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=(
            'Orange Data unauthorized: POST /api/v2/documents, '
            + 'status code 401'
        ),
        failure_id='kClientCertificateFailed',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        """
        INSERT INTO cashbox_integration.receipts(
            park_id,
            driver_id,
            order_id,
            cashbox_id,
            external_id,
            status,
            created_at,
            updated_at,
            order_price,
            order_end
        )
        VALUES (
            'park_id_1',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'uuid_1',
            'push_to_cashbox',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            '250.00',
            '2019-10-01T10:10:00'
        );

        INSERT INTO cashbox_integration.cashboxes(
            park_id,
            id,
            idempotency_token,
            date_created,
            date_updated,
            state,
            is_current,
            cashbox_type,
            details,
            secrets
        )
        VALUES (
            'park_id_1',
            'cashbox_id_1',
            'idemp_1',
            '2019-06-22 19:10:25-07',
            '2019-06-22 19:10:25-07',
            'valid',
            'TRUE',
            'orange_data',
            '{
                "tin_pd_id": "0123456789",
                "tax_scheme_type": "simple"
            }',
            '{
                "signature_private_key":
                    "3ajOAn4QH+xdo+fvE2atwbUSbsBcfFSXB4XJhcVxk5w="
            }'
        );
    """,
    ],
)
async def test_wrong_private_key(
        mockserver,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler(
        'cashbox-orange-data/api/v2/documents/0123456/status/uuid_1',
    )
    def od_get_status(request):
        return {}

    park_id, order_id, updated_at, _ = initialize()
    enable_periodic_task(taxi_config)

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    assert od_get_status.times_called == 0

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    fail_message = 'Orange Data unauthorized: Failed to load private key'
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        task_uuid=None,
        fail_message=fail_message,
        failure_id='kSignatureFailed',
    )

    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at
