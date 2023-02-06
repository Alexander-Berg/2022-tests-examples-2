import pytest

from tests_bank_cashback_processing import common

TEST_IDEMPOTENCY_TOKEN = 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df'
TEST_IDEMPOTENCY_TOKEN_WITHOUT_BASKET = '2'

TEST_KWARGS = {'idempotency_token': 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df'}


def get_history_statuses(pgsql):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select basket_status '
        f'from bank_cashback_processing.cashback_history '
        f'order by timestamp '
        f'desc ',
    )

    return list(map(lambda row: row[0], cursor.fetchall()))


async def test_stq_new_task_success(
        mockserver, stq_runner, pgsql, trust_mock, monkeypatch, _stq_mock,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/topup')
    def _basket_create_handler(request):
        assert request.method == 'POST'
        assert request.json['pass_params']['payload'] == {'has_plus': True}
        assert request.json['developer_payload'] == '{"rule_id":"rule_id"}'
        return mockserver.make_response(
            status=201, json={'purchase_token': 'purchase_token'},
        )

    trust_mock.set_payment_status('authorized')
    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == 'PAYMENT_RECEIVED'
    )

    assert _basket_create_handler.has_calls
    assert trust_mock.basket_info_handler.has_calls
    assert trust_mock.basket_start_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls
    assert get_history_statuses(pgsql) == [
        'authorized',
        'started',
        'not_started',
    ]


async def test_stq_new_task_already_ok(
        stq_runner, pgsql, trust_mock, _stq_mock,
):
    common.set_payment_status(
        pgsql, TEST_IDEMPOTENCY_TOKEN, 'PAYMENT_RECEIVED',
    )

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert not trust_mock.basket_create_handler.has_calls
    assert not trust_mock.basket_info_handler.has_calls
    assert not trust_mock.basket_start_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls


async def test_stq_new_task_without_basket(
        mockserver, stq_runner, pgsql, trust_mock, monkeypatch,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    trust_mock.set_payment_status('authorized')

    monkeypatch.setitem(
        TEST_KWARGS,
        'idempotency_token',
        TEST_IDEMPOTENCY_TOKEN_WITHOUT_BASKET,
    )
    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN_WITHOUT_BASKET)
        == 'PAYMENT_RECEIVED'
    )

    assert trust_mock.basket_create_handler.has_calls
    assert trust_mock.basket_info_handler.has_calls
    assert trust_mock.basket_start_handler.has_calls
    assert not mock_stq_reschedule.has_calls
    assert get_history_statuses(pgsql) == [
        'authorized',
        'started',
        'not_started',
    ]


async def test_stq_task_reschedule(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    trust_mock.set_payment_status('waiting')
    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'STARTED'
    )
    assert mock_stq_reschedule.has_calls
    assert get_history_statuses(pgsql) == ['waiting', 'started', 'not_started']


async def test_stq_task_basket_failed(stq_runner, pgsql, trust_mock):
    trust_mock.set_payment_status('not_authorized')
    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )
    assert common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'FAILED'
    assert get_history_statuses(pgsql) == [
        'not_authorized',
        'started',
        'not_started',
    ]


async def test_stq_bad_idempotency_token(mockserver, stq_runner):
    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id',
        kwargs={'idempotency_token': 'bad_token'},
        expect_fail=True,
    )


@pytest.mark.parametrize('status', ['CREATED', 'STARTED'])
async def test_stq_existing_basket_waiting(
        mockserver, stq_runner, pgsql, trust_mock, status,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, status=status)
    trust_mock.set_payment_status('waiting')

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert not trust_mock.basket_create_handler.has_calls
    if status == 'STARTED':
        assert not trust_mock.basket_start_handler.has_calls
    else:
        assert trust_mock.basket_start_handler.has_calls
    assert mock_stq_reschedule.has_calls
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'STARTED'
    )


@pytest.mark.parametrize('status', ['CREATED', 'STARTED'])
async def test_stq_existing_basket_authorized(
        mockserver, stq_runner, pgsql, trust_mock, status,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, status)
    trust_mock.set_payment_status('authorized')

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert not trust_mock.basket_create_handler.has_calls
    if status == 'STARTED':
        assert not trust_mock.basket_start_handler.has_calls
    else:
        assert trust_mock.basket_start_handler.has_calls
    assert not mock_stq_reschedule.has_calls
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == 'PAYMENT_RECEIVED'
    )


async def test_stq_start_basket_race(stq_runner, pgsql, trust_mock, testpoint):
    @testpoint('start_basket_race')
    def _start_basket(data):
        cursor = pgsql['bank_cashback_processing'].cursor()
        cursor.execute(
            (
                f'UPDATE bank_cashback_processing.cashbacks '
                f'SET status=\'FAILED\' '
                f'WHERE idempotency_token=\'{TEST_IDEMPOTENCY_TOKEN}\' '
            ),
        )

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )

    assert common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'FAILED'
    assert trust_mock.basket_start_handler.has_calls
    assert not trust_mock.basket_info_handler.has_calls
    assert get_history_statuses(pgsql) == ['not_started']


async def test_stq_create_basket_race(
        stq_runner, pgsql, trust_mock, testpoint,
):
    @testpoint('create_basket_race')
    def _start_basket(data):
        cursor = pgsql['bank_cashback_processing'].cursor()
        cursor.execute(
            (
                f'UPDATE bank_cashback_processing.cashbacks '
                f'SET status=\'PAYMENT_RECEIVED\' '
                f'WHERE idempotency_token=\'{TEST_IDEMPOTENCY_TOKEN}\' '
            ),
        )

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )

    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == 'PAYMENT_RECEIVED'
    )
    assert trust_mock.basket_create_handler.has_calls
    assert not trust_mock.basket_start_handler.has_calls
    assert not trust_mock.basket_info_handler.has_calls


async def trust_network_error(mockserver, stq_runner, pgsql):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/topup')
    def _basket_create_handler(request):
        return mockserver.NetworkError()

    await stq_runner.bank_cashback_charge_processing.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )

    assert not common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
    assert _mock_stq_reschedule.has_calls
