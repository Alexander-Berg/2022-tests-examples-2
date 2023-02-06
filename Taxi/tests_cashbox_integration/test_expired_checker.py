import datetime

import pytest
import pytz


from tests_cashbox_integration import utils


def initialize():
    return (
        'park_id_1',
        'task_uuid_1',
        datetime.datetime.now(pytz.timezone('Europe/Moscow')),
    )


def create_expected_receipt(
        status, order_id, external_id, task_uuid=None, fail_message=None,
):
    park_id = 'park_id_1'
    driver_id = 'driver_id_1'
    cashbox_id = 'cashbox_id_1'
    order_price = 250.00
    order_end = datetime.datetime.fromisoformat('2019-10-01T10:10:00+03:00')

    receipt = utils.create_receipt(
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
    )
    return receipt


async def test_simple(taxi_cashbox_integration, pgsql, taxi_config):
    taxi_config.set_values(
        dict(
            CASHBOX_INTEGRATION_EXPIRED_CHECKER={'enable': True, 'delay': 300},
        ),
    )

    park_id, _, updated_at = initialize()

    await taxi_cashbox_integration.run_periodic_task('ExpiredChecker0')

    order_id = 'order_id_1'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='expired', order_id=order_id, external_id='idempotency_key_1',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at

    order_id = 'order_id_2'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='expired', order_id=order_id, external_id='idempotency_key_2',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] > updated_at

    order_id = 'order_id_3'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='push_to_cashbox',
        order_id=order_id,
        external_id='idempotency_key_3',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at

    order_id = 'order_id_4'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='need_order_info',
        order_id=order_id,
        external_id='idempotency_key_4',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


async def test_with_other_status(taxi_cashbox_integration, pgsql, taxi_config):
    taxi_config.set_values(
        dict(
            CASHBOX_INTEGRATION_EXPIRED_CHECKER={'enable': True, 'delay': 300},
        ),
    )

    park_id, task_uuid, updated_at = initialize()

    await taxi_cashbox_integration.run_periodic_task('ExpiredChecker0')

    order_id = 'order_id_5'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='fail',
        order_id=order_id,
        external_id='idempotency_key_5',
        task_uuid=task_uuid,
        fail_message='fail message',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at

    order_id = 'order_id_6'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='complete',
        order_id=order_id,
        external_id='idempotency_key_6',
        task_uuid=task_uuid,
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at

    order_id = 'order_id_7'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='expired',
        order_id=order_id,
        external_id='idempotency_key_7',
        task_uuid=task_uuid,
        fail_message='fail message',
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at

    order_id = 'order_id_8'
    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)
    expected_receipt = create_expected_receipt(
        status='wait_status',
        order_id=order_id,
        external_id='idempotency_key_8',
        task_uuid=task_uuid,
    )
    utils.compare_receipt(receipt, expected_receipt)
    assert receipt['updated_at'] <= updated_at


def get_external_id_ck(ck_request):
    return ck_request['request'].headers['X-Request-ID']


def check_requests_post_to_cashbox(ck_cashbox_handle, expected_external_id):
    request = ck_cashbox_handle.next_call()
    external_id = get_external_id_ck(request)

    assert external_id == expected_external_id


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
            order_end,
            task_uuid,
            fail_message
        )
        VALUES(
            'park_id_1',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'idempotency_key_1',
            'push_to_cashbox',
            CURRENT_TIMESTAMP -  interval '320 seconds',
            CURRENT_TIMESTAMP,
            '250.00',
            '2019-10-01T10:10:00',
            NULL,
            NULL
        ),
        (
            'park_id_1',
            'driver_id_1',
            'order_id_2',
            'cashbox_id_1',
            'idempotency_key_2',
            'push_to_cashbox',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            '250.00',
            '2019-10-01T10:10:00',
            NULL,
            NULL
        );
        """,
        """
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
            'cloud_kassir',
            '{
                "tin_pd_id": "0123456789",
                "tax_scheme_type": "simple"
            }',
            '{
                "public_id": "M5a7svvcrnA7E5axBDY2sw==",
                "api_secret": "dCKumeJhRuUkLWmKppFyPQ=="
            }'
        );
        """,
    ],
)
async def test_valid_time_interval_push_to_cashbox(
        mockserver,
        atol_get_token,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt')
    def ck_post_receipt(request):
        return mockserver.make_response(status=500)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_EXPIRED_CHECKER': {
                'enable': False,
                'delay': 300,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    check_requests_post_to_cashbox(ck_post_receipt, 'idempotency_key_2')
