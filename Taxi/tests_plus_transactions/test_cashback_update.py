import typing

import pytest


async def post_cashback_update(
        taxi_plus_transactions,
        load_json,
        request_file_name='taxi_cashback_update_request_body.json',
        service_id='taxi',
        version=1,
):
    request_body = load_json(request_file_name)
    request_body['service_id'] = service_id
    request_body['version'] = version
    return await taxi_plus_transactions.post(
        '/plus-transactions/v1/cashback/update', json=request_body,
    )


async def test_cashback_update_no_services_config(
        taxi_plus_transactions, load_json,
):
    resp = await post_cashback_update(taxi_plus_transactions, load_json)
    assert resp.status == 500


@pytest.mark.experiments3(filename='config3_plus_transactions_services.json')
@pytest.mark.parametrize(
    'service_id, err_msg',
    [
        pytest.param(
            'service_id_not_exist',
            'Bad Request: Service info not found in plus_transactions_services config for service_id=service_id_not_exist',  # noqa: E501
            id='service_id_not_in_config',
        ),
    ],
)
async def test_cashback_update_invalid_services_config(
        taxi_plus_transactions, load_json, service_id, err_msg,
):
    resp = await post_cashback_update(
        taxi_plus_transactions, load_json, service_id=service_id,
    )
    assert resp.status == 400
    assert resp.json()['message'] == err_msg


class MyTestCase(typing.NamedTuple):
    req_version: int = 1

    request_file_name: str = 'taxi_cashback_update_request_body.json'
    has_invoice: bool = True
    id_namespace: str = 'cashback_levels'
    billing_service: str = 'card'
    create_invoice_resp_code: int = 200
    has_cashback_in_invoice: bool = True
    cashback_status: str = 'init'
    cashback_rewarded: typing.List = []
    cashback_version: int = 1

    update_cashback_amount: str = '100'
    update_cashback_source: str = 'taxi'
    update_cashback_wallet: str = 'wallet_id_1'
    update_fiscal_nds: typing.Optional[str] = None
    update_fiscal_title: typing.Optional[str] = None
    update_cashback_resp_code: int = 200

    resp_code: int = 200
    resp_err_msg: str = ''


@pytest.mark.experiments3(filename='config3_plus_transactions_services.json')
@pytest.mark.parametrize(
    'user_has_wallet, is_z_wallet',
    [
        pytest.param(True, False, id='existing_wallet'),
        pytest.param(True, True, id='z-wallet'),
        pytest.param(False, False, id='no_wallet'),
    ],
)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                has_invoice=False,
                create_invoice_resp_code=400,
                resp_code=400,
                resp_err_msg='Bad Request',
            ),
            id='create_invoice_bad_request',
        ),
        pytest.param(
            MyTestCase(
                req_version=0,
                has_invoice=False,
                create_invoice_resp_code=409,
                resp_code=409,
                resp_err_msg='Race Condition',
            ),
            id='create_invoice_race_condition',
        ),
        pytest.param(
            MyTestCase(
                has_cashback_in_invoice=False,
                resp_code=500,
                resp_err_msg='Internal Server Error',
            ),
            id='no_cashback_in_invoice',
        ),
        pytest.param(
            MyTestCase(
                req_version=1,
                cashback_version=2,
                resp_code=409,
                resp_err_msg='Race Condition: invalid version: 1',
            ),
            id='invoice_cashback_invalid_version',
        ),
        pytest.param(
            MyTestCase(
                cashback_status='in-progress',
                resp_code=409,
                resp_err_msg='Race Condition: current cashback operation is still in progress, can\'t start a new one until current is done',  # noqa: E501
            ),
            id='cashback_status_in_progress',
        ),
        pytest.param(
            MyTestCase(
                cashback_rewarded=[{'source': 'taxi', 'amount': '100'}],
                resp_code=200,
            ),
            id='no_cashback_update_needed',
        ),
        pytest.param(
            MyTestCase(
                cashback_rewarded=[{'source': 'taxi', 'amount': '100'}],
                cashback_status='failed',
                resp_code=200,
            ),
            id='cashback_update_needed_if_last_operation_failed',
        ),
        pytest.param(
            MyTestCase(
                update_cashback_resp_code=400,
                resp_code=400,
                resp_err_msg='Bad Request',
            ),
            id='update_cashback_bad_request',
        ),
        pytest.param(
            MyTestCase(
                update_cashback_resp_code=409,
                resp_code=409,
                resp_err_msg='Race Condition',
            ),
            id='update_cashback_race_condition',
        ),
        pytest.param(
            MyTestCase(
                update_cashback_resp_code=429,
                resp_code=500,
                resp_err_msg='Internal Server Error',
            ),
            id='update_cashback_rate_limit_exceeded',
        ),
        pytest.param(MyTestCase(), id='ok_taxi'),
        pytest.param(
            MyTestCase(
                id_namespace='kinopoisk_personal_goals',
                billing_service='kinopoisk',
                request_file_name=(
                    'kinopoisk_cashback_update_request_body.json'
                ),
                update_cashback_source='kinopoisk',
                update_fiscal_nds='nds_none',
                update_fiscal_title='Кешбэк',
            ),
            id='ok_kinopoisk_with_fiscal',
        ),
        pytest.param(
            MyTestCase(
                id_namespace='eda_personal_goals',
                billing_service='food_payment',
                request_file_name='eda_cashback_update_request_body.json',
                update_cashback_source='eda',
            ),
            id='ok_eda',
        ),
        pytest.param(
            MyTestCase(
                id_namespace='lavka_personal_goals',
                billing_service='food_payment',
                request_file_name='lavka_cashback_update_request_body.json',
                update_cashback_source='lavka',
            ),
            id='ok_lavka',
        ),
        pytest.param(
            MyTestCase(
                id_namespace='market_personal_goals',
                billing_service='market',
                request_file_name='market_cashback_update_request_body.json',
                update_cashback_source='market',
            ),
            id='ok_market',
        ),
        pytest.param(
            MyTestCase(
                id_namespace='music_personal_goals',
                billing_service='music',
                request_file_name='music_cashback_update_request_body.json',
                update_cashback_source='music',
            ),
            id='ok_music',
        ),
        pytest.param(
            MyTestCase(
                request_file_name='invalid_cashback_update_request_body.json',
                resp_code=400,
                resp_err_msg='Value of discriminator \'service_not_exist\' for path \'/\' does not match any known mapping',  # noqa: E501
            ),
            id='update_cashback_invalid_payload',
        ),
    ],
)
async def test_cashback_update(
        taxi_plus_transactions,
        mockserver,
        load_json,
        transactions_ng_fixt,
        user_has_wallet,
        is_z_wallet,
        case: MyTestCase,
):
    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _mock_plus_wallet_balances(request):
        assert request.query['yandex_uid'] == 'yandex_uid_1'
        assert request.query['currencies'] == 'RUB'

        if user_has_wallet:
            wallet_id = 'wallet_id_1' if not is_z_wallet else 'z_wallet_id_1'
            return {
                'balances': [
                    {
                        'wallet_id': wallet_id,
                        'balance': '0',
                        'currency': 'RUB',
                    },
                ],
            }
        return {'balances': []}

    @mockserver.json_handler('/plus-wallet/v1/create')
    def _mock_billing_wallet_create(request):
        assert request.json['yandex_uid'] == 'yandex_uid_1'
        assert request.json['currency'] == 'RUB'
        assert request.json['user_ip'] == ''
        return {'wallet_id': 'wallet_id_1'}

    transactions_ng_fixt.has_invoice = case.has_invoice
    transactions_ng_fixt.id_namespace = case.id_namespace
    transactions_ng_fixt.billing_service = case.billing_service
    transactions_ng_fixt.create_invoice_resp_code = (
        case.create_invoice_resp_code
    )
    transactions_ng_fixt.has_cashback_in_invoice = case.has_cashback_in_invoice
    transactions_ng_fixt.cashback_status = case.cashback_status
    transactions_ng_fixt.cashback_rewarded = case.cashback_rewarded
    transactions_ng_fixt.cashback_version = case.cashback_version

    transactions_ng_fixt.update_cashback_amount = case.update_cashback_amount
    transactions_ng_fixt.update_cashback_source = case.update_cashback_source
    transactions_ng_fixt.update_cashback_wallet = case.update_cashback_wallet
    transactions_ng_fixt.update_fiscal_nds = case.update_fiscal_nds
    transactions_ng_fixt.update_fiscal_title = case.update_fiscal_title
    transactions_ng_fixt.update_cashback_resp_code = (
        case.update_cashback_resp_code
    )

    resp = await post_cashback_update(
        taxi_plus_transactions,
        load_json,
        request_file_name=case.request_file_name,
        service_id=case.update_cashback_source,
        version=case.req_version,
    )
    assert resp.status == case.resp_code

    if case.resp_err_msg:
        resp_body = resp.json()
        assert resp_body['code'] == str(case.resp_code)
        assert case.resp_err_msg in resp_body['message']
    else:
        if not transactions_ng_fixt.mock_update_cashback.has_calls:
            return
        update_call = transactions_ng_fixt.mock_update_cashback.next_call()
        request = update_call['request']

        expected_payload = load_json(case.request_file_name)[
            'amount_by_source'
        ][case.update_cashback_source]['payload']
        cashback_source = request.json['sources'][case.update_cashback_source]
        assert (
            cashback_source['cashback_type']
            == expected_payload['cashback_type']
        )
        assert cashback_source.get('product_id') == expected_payload.get(
            'product_id',
        )

        actual_payload = cashback_source['extra_payload']
        assert actual_payload == expected_payload
