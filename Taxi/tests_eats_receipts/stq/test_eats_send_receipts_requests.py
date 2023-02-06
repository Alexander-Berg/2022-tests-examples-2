import psycopg2
import pytest

TEST_ORIGINATOR_CONFIG = {
    'eats-payment': {
        'url': {'$mockserver': '/v1/receipts/retrieve'},
        'tvm_name': 'eats-payments',
    },
    'eats-core': {
        'url': '/v1/core-receipts/retrieve',
        'tvm_name': 'eats-core',
    },
}

TEST_TVM_CONFIG = {
    'eats-payments': 2021618,
    'stq-agent': 2013178,
    'statistics': 201321,
    'personal': 201322,
}


def request_handler(request):
    if 'break' in request.json['document_id']:
        country_code = 'FB'
    else:
        country_code = 'RU'
    return {
        'is_refund': True,
        'order': {
            'country_code': country_code,
            'order_nr': 'test_order',
            'payment_method': 'card',
        },
        'products': [
            {
                'id': 'big_mac',
                'price': '5.00',
                'supplier_inn': '479753957665',
                'tax': '20',
                'title': 'Big Mac Burger',
            },
        ],
        'user_info': {
            'personal_email_id': 'mail_id',
            'personal_phone_id': 'phone_id',
        },
    }


@pytest.fixture(name='receipt_good_response')
async def _mock_receipt_good_response(mockserver):
    def _inner(user_info=None):
        @mockserver.json_handler('/v1/receipts/retrieve')
        def _mock_handler(request):
            result = request_handler(request)
            if user_info is not None:
                result['user_info'] = user_info

            return result

        return _mock_handler

    return _inner


@pytest.fixture(name='receipt_invalid_inn')
async def mock_receipt_invalid_inn(mockserver):
    @mockserver.json_handler('/v1/receipts/retrieve')
    def _mock_handler(request):
        response = request_handler(request)
        response['products'][0]['supplier_inn'] = '479753957765'


@pytest.fixture(name='receipt_malformed_response')
async def mock_receipt_malformed_response(mockserver):
    @mockserver.json_handler('/v1/receipts/retrieve')
    def _mock_handler(request):
        assert request.json == {
            'document_id': 'test_order/refund/create:100500',
        }
        return {'foob': 'ar'}


@pytest.fixture(name='receipt_failed_response')
async def mock_receipt_failed_response(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/v1/receipts/retrieve')
        def _mock_handler(request):
            return mockserver.make_response('bad request', status=status)

    return wrapper


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
@pytest.mark.parametrize(
    'user_info, user_info_from_bd',
    (
        (
            {'personal_email_id': 'mail_id', 'personal_phone_id': 'phone_id'},
            '(mail_id,phone_id)',
        ),
        ({'personal_email_id': 'mail_id'}, '(mail_id,)'),
        ({'personal_phone_id': 'phone_id'}, '(,phone_id)'),
    ),
)
async def test_successful_config_lookup(
        stq_runner,
        receipt_good_response,
        pgsql,
        stq,
        user_info,
        user_info_from_bd,
):
    mock_receipt_good_response = receipt_good_response(user_info)
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['test_order/refund/create:100500', 'eats-payment'],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    receipt_request = cursor.fetchone()
    assert receipt_request['document_id'] == 'test_order/refund/create:100500'
    assert receipt_request['created_at'] is not None
    assert receipt_request['created_at'] == receipt_request['updated_at']
    assert receipt_request['status'] == 'created'
    assert receipt_request['user_info'] == user_info_from_bd
    assert receipt_request['order_info'] == '(RU,card)'
    assert receipt_request['order_id'] == 'test_order'

    assert stq.eats_send_receipt.times_called == 1
    assert mock_receipt_good_response.times_called == 1


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_insert_same_request_twice(
        stq_runner, receipt_good_response, pgsql, stq,
):
    receipt_good_response()
    new_document_id = 'test_order/refund/create:100500'

    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=[new_document_id, 'eats-payment'],
    )

    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=[new_document_id, 'eats-payment'],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT COUNT(*) FROM eats_receipts.send_receipt_requests')
    receipt_requests_count = cursor.fetchone()
    assert receipt_requests_count[0] == 1

    assert stq.eats_send_receipt.times_called == 1


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_malformed_response_received(
        stq_runner, receipt_malformed_response, pgsql,
):
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['test_order/refund/create:100500', 'eats-payment'],
        expect_fail=True,
    )


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_malformed_inn_received(stq_runner, receipt_invalid_inn, pgsql):
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['test_order/refund/create:100500', 'eats-payment'],
        expect_fail=True,
    )


@pytest.mark.parametrize(
    'status, expect_fail, fail_count', ((403, False, 1), (404, True, 1)),
)
@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_failed_handle_response(
        stq_runner,
        taxi_eats_receipts,
        receipt_failed_response,
        taxi_eats_receipts_monitor,
        status,
        expect_fail,
        fail_count,
):
    await taxi_eats_receipts.tests_control(reset_metrics=True)
    receipt_failed_response(status=status)
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['test_order/refund/create:100500', 'eats-payment'],
        expect_fail=expect_fail,
    )
    metrics_name = 'originators-errors'
    metrics = await taxi_eats_receipts_monitor.get_metrics(metrics_name)
    assert metrics['originators-errors'] == {
        '$meta': {'solomon_children_labels': 'originator'},
        'eats-payment': fail_count,
        'stable-originator': 0,
    }


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_failed_config_lookup(stq_runner):
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['1', 'pineapple'],
        expect_fail=True,
    )


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_successful_config_lookup_unsupported_country(
        stq_runner, receipt_good_response, pgsql, stq,
):
    receipt_good_response()
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=['test_order/refund/break:100500', 'eats-payment'],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    assert not list(cursor)
    assert stq.eats_send_receipt.times_called == 0
