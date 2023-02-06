import datetime as dt

import pytest


@pytest.mark.parametrize(
    'debt_id, extra_stq_kwargs, update_times_called, stq_eta, check_stq_call, '
    'retrieve_response_path',
    [
        pytest.param(
            'collect_debt_id',
            {},
            1,
            None,
            True,
            'retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        pytest.param(
            'collect_interval_debt_id',
            {},
            1,
            None,
            True,
            'retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        pytest.param(
            'collect_debt_id',
            {},
            0,
            None,
            False,
            'paid_handled_previous_version_retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        pytest.param(
            'collect_debt_id',
            {},
            0,
            None,
            False,
            'no_attempts_left_retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        # debt not found, plan_in_advance_params allows reschedule
        pytest.param(
            'not_created_collect_debt_id',
            {
                'plan_in_advance_params': {
                    'planned_at': '2021-06-29T23:00:00+00:00',
                },
            },
            0,
            dt.datetime(2021, 6, 30),
            False,
            None,
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        # debt not found, plan_in_advance_params doesn't allow reschedule
        pytest.param(
            'not_created_collect_debt_id',
            {
                'plan_in_advance_params': {
                    'planned_at': '2021-06-29T22:59:59+00:00',
                },
            },
            0,
            None,
            False,
            None,
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        # invoice is active, reschedule
        pytest.param(
            'collect_debt_id',
            {},
            0,
            dt.datetime(2021, 6, 30),
            False,
            'active_retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        # unhandled debt callback, reschedule
        pytest.param(
            'collect_debt_id',
            {},
            0,
            dt.datetime(2021, 6, 30),
            False,
            'paid_previous_version_retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
        # too early to call /update, stq.call_later
        pytest.param(
            'collect_debt_id',
            {},
            0,
            dt.datetime(2021, 1, 1),
            True,
            'retrieve_response.json',
            marks=pytest.mark.now('2020-01-01T00:00:00+00:00'),
        ),
        (
            'collect_debt_id',
            {},
            0,
            None,
            True,
            'later_debt_retrieve_response.json',
        ),
        (
            'collect_zero_debt_id',
            {},
            0,
            None,
            True,
            'paid_debt_retrieve_response.json',
        ),
        pytest.param(
            'collect_debt_id',
            {},
            1,
            None,
            True,
            'paid_debt_retrieve_response.json',
            marks=pytest.mark.now('2021-06-30T00:00:00+00:00'),
        ),
    ],
)
@pytest.mark.pgsql('eats_debt_collector', files=['collect_debt.sql'])
@pytest.mark.config(
    DEBT_COLLECTOR_TRANSACTIONS_INSTALLATIONS={
        'eda': {
            'base_url': {'$mockserver': '/transactions-eda'},
            'tvm_name': 'transactions',
        },
    },
)
async def test_collect_debt(
        stq_runner,
        stq,
        mockserver,
        load_json,
        debt_id,
        extra_stq_kwargs,
        update_times_called,
        stq_eta,
        check_stq_call,
        retrieve_response_path,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def retrieve(request):
        assert request.json == {
            'id': 'collect_debt_invoice_id',
            'id_namespace': 'eda_namespace',
            'prefer_transactions_data': False,
        }
        return load_json(retrieve_response_path)

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def update(request):
        expected = load_json('update_request.json')
        expected['notification_payload']['debt_id'] = debt_id
        assert request.json == expected
        return {}

    await stq_runner.collect_debt.call(
        task_id=debt_id,
        kwargs={'debt_id': debt_id, 'service': 'eats', **extra_stq_kwargs},
    )
    assert retrieve.times_called == (1 if retrieve_response_path else 0)
    assert update.times_called == update_times_called
    if stq_eta is None:
        assert stq.collect_debt.times_called == 0
    else:
        assert stq.collect_debt.times_called == 1
        stq_call = stq.collect_debt.next_call()
        assert stq_call['id'] == debt_id
        if check_stq_call:
            assert stq_call['kwargs']['debt_id'] == debt_id
            assert stq_call['kwargs']['service'] == 'eats'
            assert stq_call['eta'] == stq_eta
