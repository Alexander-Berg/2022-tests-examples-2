import typing

import pytest


async def post_cashback_status(
        taxi_plus_transactions,
        ext_ref_id='ext_ref_id_1',
        service_id='taxi',
        consumer='consumer_1',
):
    return await taxi_plus_transactions.post(
        '/plus-transactions/v1/cashback/status',
        params={
            'ext_ref_id': ext_ref_id,
            'service_id': service_id,
            'consumer': consumer,
        },
    )


async def test_cashback_status_no_services_config(taxi_plus_transactions):
    resp = await post_cashback_status(taxi_plus_transactions)
    assert resp.status == 500


@pytest.mark.experiments3(filename='config3_plus_transactions_services.json')
@pytest.mark.parametrize(
    'service_id, err_msg',
    [
        pytest.param(
            'service_id_not_exist',
            'Service info not found in plus_transactions_services config for service_id=service_id_not_exist',  # noqa: E501
            id='service_id_not_in_config',
        ),
    ],
)
async def test_cashback_status_invalid_services_config(
        taxi_plus_transactions, service_id, err_msg,
):
    resp = await post_cashback_status(
        taxi_plus_transactions, service_id=service_id,
    )
    assert resp.status == 400
    assert resp.json()['message'] == err_msg


class MyTestCase(typing.NamedTuple):
    has_invoice: bool = True
    has_cashback_in_invoice: bool = True
    cashback_status: str = 'init'
    cashback_amount: str = '0'
    cashback_operations: typing.List = []
    cashback_version: int = 1
    resp_code: int = 200
    resp_err_msg: str = ''


@pytest.mark.experiments3(filename='config3_plus_transactions_services.json')
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(has_invoice=False), id='no_invoice'),
        pytest.param(
            MyTestCase(has_cashback_in_invoice=False),
            id='no_cashback_in_invoice',
        ),
        pytest.param(
            MyTestCase(cashback_status='init'), id='cashback_status_init',
        ),
    ],
)
async def test_cashback_status(
        taxi_plus_transactions, transactions_ng_fixt, case,
):
    transactions_ng_fixt.has_invoice = case.has_invoice
    transactions_ng_fixt.has_cashback_in_invoice = case.has_cashback_in_invoice
    transactions_ng_fixt.cashback_status = case.cashback_status
    transactions_ng_fixt.cashback_version = case.cashback_version

    resp = await post_cashback_status(taxi_plus_transactions)
    assert resp.status == case.resp_code

    resp_body = resp.json()
    if case.resp_err_msg:
        assert resp_body['code'] == str(case.resp_code)
        assert resp_body['message'] == case.resp_err_msg
    else:
        assert resp_body['status'] == case.cashback_status
        assert resp_body['version'] == case.cashback_version
        assert resp_body['amount'] == case.cashback_amount
        assert resp_body.get('operations', []) == case.cashback_operations
