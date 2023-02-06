# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
import dataclasses
import datetime

import pytest

from taxi.stq import async_worker_ng

from corp_clients.stq import contract_debt_payoff


NOW = datetime.date(2021, 11, 29)


@pytest.fixture
def get_orders_info_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_orders_info')
    async def _get_orders_info(contract_id, **kwargs):
        return [{'ServiceID': 777, 'ServiceOrderID': 'service_order_id'}]


@pytest.fixture
def create_request2_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.create_request2')
    async def _create_request2(
            operator_uid, client_id, billing_order, optional_args,
    ):
        return {'RequestID': 'request_id'}


@pytest.fixture
def pay_request_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.pay_request')
    async def _pay_request(operator_uid, optional_args):
        return {'transaction_id': 'transaction_id'}


@pytest.fixture
def mock_balance(patch):
    class MockBalance:
        @dataclasses.dataclass
        class BalanceData:
            resp_code: str

        data = BalanceData(resp_code='')

        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.check_request_payment')
        async def _check_request_payment(operator_uid, optional_args):
            return {'resp_code': MockBalance.data.resp_code}

    return MockBalance()


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['resp_code', 'expected_status', 'debt_id'],
    [
        pytest.param('success', 'finished', '101', id='success'),
        pytest.param(
            'restricted_card', 'failed_trylater', '101', id='restricted_card',
        ),
        pytest.param(
            'not_enough_funds', 'failed_trylater', '101', id='failed_trylater',
        ),
        pytest.param('success', 'finished', '102', id='success102'),
    ],
)
async def test_debt_payoff(
        mockserver,
        patch,
        db,
        stq3_context,
        stq,
        get_orders_info_mock,
        create_request2_mock,
        pay_request_mock,
        mock_balance,
        resp_code,
        expected_status,
        debt_id,
):
    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='corp_contract_debt_payoff',
    )

    mock_balance.data.resp_code = resp_code

    debt_info = {'_id': debt_id}

    await contract_debt_payoff.task(
        stq3_context, task_meta_info=task_info, debt_info=debt_info,
    )

    debts = await db.corp_contract_debts.find({'_id': debt_id}).to_list(None)

    assert len(debts) == 1
    assert (
        debts[0]['payoff_status'] == expected_status
        and debts[0]['transaction_id'] == 'transaction_id'
    )

    assert 'last_pay_request' in debts[0]
    assert 'service_id' in debts[0]

    if resp_code == 'restricted_card':
        restricted_cards = await db.corp_cards_restricted.find({}).to_list(
            None,
        )
        assert restricted_cards


@pytest.mark.now(NOW.isoformat())
async def test_debt_payoff_customraise(
        mockserver,
        patch,
        db,
        stq3_context,
        stq,
        get_orders_info_mock,
        create_request2_mock,
        pay_request_mock,
        mock_balance,
):
    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='corp_contract_debt_payoff',
    )

    mock_balance.data.resp_code = 'operation_in_progress'

    debt_info = {'_id': '101'}

    flag = False

    try:
        await contract_debt_payoff.task(
            stq3_context, task_meta_info=task_info, debt_info=debt_info,
        )
    except contract_debt_payoff.PayRequestFailed:
        flag = True

    assert flag

    debts = await db.corp_contract_debts.find({'_id': '101'}).to_list(None)

    assert (
        debts[0]['payoff_status'] == 'failed_technical'
        and debts[0]['transaction_id'] == 'transaction_id'
    )

    assert 'last_pay_request' in debts[0]


@pytest.mark.now(NOW.isoformat())
async def test_debt_payoff_reschedule(
        mockserver,
        patch,
        db,
        stq3_context,
        stq,
        get_orders_info_mock,
        create_request2_mock,
        pay_request_mock,
        mock_balance,
):
    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='corp_contract_debt_payoff',
    )

    mock_balance.data.resp_code = None

    debt_info = {'_id': '101'}

    await contract_debt_payoff.task(
        stq3_context, task_meta_info=task_info, debt_info=debt_info,
    )

    call = stq.corp_contract_debt_payoff.next_call()
    assert call['id'] == 'task_id'

    debts = await db.corp_contract_debts.find({'_id': '101'}).to_list(None)

    assert (
        debts[0]['payoff_status'] == 'started'
        and debts[0]['transaction_id'] == 'transaction_id'
    )

    assert 'last_pay_request' in debts[0]
