import pytest


def test_claim_context(load_json, claim_context_result):
    filename = 'flow_claims/claim_billing_context.json'
    assert claim_context_result == {'context': load_json(filename)}


@pytest.mark.parametrize(
    ['remove_claims_field'],
    [pytest.param('corp_client_id', id='corp_client_id')],
    indirect=['remove_claims_field'],
)
async def test_yandex_go_claim_context(
        remove_claims_field,
        mockserver,
        load_json,
        build_claim_context,
        claim_id,
        update_claims_field,
):
    methods_url = (
        '/cargo-claims/v2/claims/finance/estimation-result/payment-methods'
    )

    @mockserver.json_handler(methods_url)
    def _(request):
        return mockserver.make_response(status=404)

    update_claims_field(
        'c2c_data',
        {
            'cargo_c2c_order_id': '3b8d1af142664fde824626a7c19e2bd9',
            'payment_method_id': 'card-5e36732e2bc54e088b1466e08e31c486',
            'payment_type': 'card',
        },
    )
    update_claims_field('yandex_uid', '439029402')
    filename = 'flow_claims/yandex_go_claim_billing_context.json'
    assert await build_claim_context(claim_id) == {
        'context': load_json(filename),
    }


async def test_yandex_go_phoenix_claim_context(
        mock_claims_estimated_payment_methods,
        build_claim_context,
        claim_id,
        update_claims_field,
):

    update_claims_field(
        'c2c_data',
        {
            'cargo_c2c_order_id': '3b8d1af142664fde824626a7c19e2bd9',
            'payment_method_id': 'card-5e36732e2bc54e088b1466e08e31c486',
            'payment_type': 'corpcard',
        },
    )
    await build_claim_context(claim_id)
    assert mock_claims_estimated_payment_methods.times_called == 1


def test_call_claims_for_claim_context(
        mock_claims_full, claim_context_result, claim_id,
):
    assert mock_claims_full.times_called == 1
    request = mock_claims_full.next_call()['request']
    assert request.query == {'claim_id': claim_id}


async def test_claim_context_event(
        mock_procaas_create,
        procaas_extract_token,
        claim_id,
        claim_context_result,
        save_claim_context,
        assert_correct_scope_queue,
):
    context = claim_context_result['context']
    kind = 'claim_billing_context'
    event_id = '123'
    expected_token = '{}_{}'.format(kind, event_id)

    await save_claim_context(claim_id, context, event_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert_correct_scope_queue(request)
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': kind, 'data': context}


def test_contractor_context(load_json, contractor_context_result):
    filename = 'flow_claims/contractor_billing_context.json'
    context = load_json(filename)
    context['country'] = 'RUS'
    context['fiscal_receipt_info']['tin'] = '085715582283'
    assert contractor_context_result == {'context': context}


def test_contractor_context_kz(
        load_json, mock_py2_fiscal_data_kz, contractor_context_result,
):
    filename = 'flow_claims/contractor_billing_context.json'
    kz_context = load_json(filename)
    kz_context['fiscal_receipt_info']['vat'] = None
    kz_context['fiscal_receipt_info'][
        'personal_tin_id'
    ] = '2201208428a9412eb6543c5433064ec9'
    kz_context['country'] = 'RUS'
    kz_context['fiscal_receipt_info']['tin'] = '091240006400'
    assert contractor_context_result == {'context': kz_context}


def test_contractor_context_none(
        load_json, mock_py2_fiscal_data_none, contractor_context_result,
):
    filename = 'flow_claims/contractor_billing_context.json'
    kz_context = load_json(filename)
    kz_context.pop('fiscal_receipt_info', None)
    assert contractor_context_result == {'context': kz_context}


def test_contractor_context_null(
        load_json, mock_py2_fiscal_data_null, contractor_context_result,
):
    filename = 'flow_claims/contractor_billing_context.json'
    context = load_json(filename)
    context.pop('fiscal_receipt_info', None)
    assert contractor_context_result == {'context': context}


def test_call_py2_products(
        claim_doc, mock_py2_products, contractor_context_result,
):
    assert mock_py2_products.times_called == 1
    request = mock_py2_products.next_call()['request']
    assert request.query == {}
    assert request.json == {
        'park_clid': 'clid2222222222222222222222222222',
        'timestamp': claim_doc['created_ts'],  # because due is absent
    }


def test_call_claims_for_contractor(
        mock_claims_full, contractor_context_result, claim_id,
):
    assert mock_claims_full.times_called == 1
    request = mock_claims_full.next_call()['request']
    assert request.query == {'parts': 'performer_info', 'claim_id': claim_id}


def test_no_context_if_park_not_found(
        set_park_not_found, contractor_context_result,
):
    assert contractor_context_result == {
        'fail_reason': {
            'code': 'park_not_found',
            'message': 'Park not found',
            'details': {},
        },
    }


@pytest.mark.parametrize(
    ['filter_py2_products_kinds', 'message_ending'],
    [
        pytest.param([], 'ride, tips', id='ride_tips'),
        pytest.param(['ride'], 'tips', id='tips'),
        pytest.param(['tips'], 'ride', id='ride'),
    ],
    indirect=['filter_py2_products_kinds'],
)
def test_no_context_if_products_absent(
        filter_py2_products_kinds, contractor_context_result, message_ending,
):
    code = 'billing_products_absent'
    message = 'Required billing products are absent: {}'.format(message_ending)
    assert contractor_context_result == {
        'fail_reason': {'code': code, 'message': message, 'details': {}},
    }


@pytest.mark.parametrize(
    ['remove_claims_field', 'message_ending'],
    [
        pytest.param('taxi_order_id', 'taxi_order_id', id='taxi_order_id'),
        pytest.param('performer_info', 'performer_info', id='perfomer_info'),
    ],
    indirect=['remove_claims_field'],
)
def test_no_context_if_taxi_info_absent(
        remove_claims_field, contractor_context_result, message_ending,
):
    code = 'taxi_info_absent'
    message = 'Required taxi order info is absent: {}'.format(message_ending)
    assert contractor_context_result == {
        'fail_reason': {'code': code, 'message': message, 'details': {}},
    }


async def test_contractor_context_event(
        mock_procaas_create,
        procaas_extract_token,
        claim_id,
        contractor_context_result,
        save_contractor_context,
        assert_correct_scope_queue,
):
    context = contractor_context_result['context']
    kind = 'contractor_billing_context'
    event_id = '123'
    expected_token = '{}_{}'.format(kind, event_id)

    await save_contractor_context(claim_id, context, event_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert_correct_scope_queue(request)
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': kind, 'data': context}


async def test_order_billing_context_request(
        build_taxi_order_billing_context,
        mock_py2_taxi_order_context,
        taxi_order_id,
):
    response = await build_taxi_order_billing_context()

    assert mock_py2_taxi_order_context.mock.times_called == 1
    request = mock_py2_taxi_order_context.mock.next_call()['request']
    assert request.json == {'order_id': taxi_order_id}

    assert response.status_code == 200
    assert 'context' in response.json()


@pytest.mark.parametrize(
    ['remove_claims_field'],
    [pytest.param('taxi_order_id', id='taxi_order_id')],
    indirect=['remove_claims_field'],
)
async def test_order_billing_context_request_no_context(
        remove_claims_field,
        build_taxi_order_billing_context,
        mock_py2_taxi_order_context,
        taxi_order_id,
):
    response = await build_taxi_order_billing_context()

    assert mock_py2_taxi_order_context.mock.times_called == 0
    assert response.status_code == 404
    assert response.json() == {
        'fail_reason': {
            'code': 'taxi_info_absent',
            'message': 'Required taxi order info is absent: taxi_order_id',
            'details': {},
        },
    }


async def test_order_billing_context_py2_returns404(
        build_taxi_order_billing_context,
        mock_py2_taxi_order_context,
        taxi_order_id,
):
    mock_py2_taxi_order_context.code = 404
    response = await build_taxi_order_billing_context()

    assert mock_py2_taxi_order_context.mock.times_called == 1
    request = mock_py2_taxi_order_context.mock.next_call()['request']
    assert request.json == {'order_id': taxi_order_id}
    assert response.status_code == 404
    assert response.json() == {
        'fail_reason': {
            'code': 'order_event_context_not_found',
            'message': 'Order event context not found',
            'details': {},
        },
    }


@pytest.mark.config(CARGO_FINANCE_ENABLE_USING_ORDER_STATUSES=True)
async def test_order_billing_context_status_matching(
        build_taxi_order_billing_context,
        mock_py2_taxi_order_context,
        taxi_config,
        taxi_cargo_finance,
        update_claims_field,
):
    claim_status = 'cancelled_with_payment'
    order_status = 'cancelled'
    order_taxi_status = 'driving'
    update_claims_field('status', claim_status)
    taxi_config.set_values(
        {
            'CARGO_FINANCE_CLAIM_STATUSES_MATCHER': {
                claim_status: {
                    'status': order_status,
                    'taxi_status': order_taxi_status,
                },
            },
        },
    )
    await taxi_cargo_finance.invalidate_caches()

    response = await build_taxi_order_billing_context()
    assert response.status_code == 200
    assert response.json()['context']['status'] == order_status
    assert response.json()['context']['taxi_status'] == order_taxi_status


@pytest.mark.config(CARGO_FINANCE_ENABLE_USING_ORDER_STATUSES=False)
async def test_order_billing_context_fails_match_status_without_fallback(
        build_taxi_order_billing_context, mock_py2_taxi_order_context,
):
    response = await build_taxi_order_billing_context()
    assert response.status_code == 500


async def test_pricing_billing_context(
        build_pricing_billing_context, mock_v1_taxi_calc_retrieve, calc_id,
):
    response = await build_pricing_billing_context()

    assert mock_v1_taxi_calc_retrieve.times_called == 1
    request = mock_v1_taxi_calc_retrieve.next_call()['request']
    assert request.json['calc_id'] == calc_id

    assert response.status_code == 200


@pytest.fixture(name='contractor_context_result')
async def _contractor_context_result(
        build_contractor_context, mock_v1_parks_retrieve, claim_id,
):
    return await build_contractor_context(claim_id)


@pytest.fixture(name='build_contractor_context')
def _build_contractor_context(build_context_factory):
    url = '/internal/cargo-finance/flow/claims/func/contractor-billing-context'
    return build_context_factory(url)


@pytest.fixture(name='claim_context_result')
async def _claim_context_result(build_claim_context, claim_id):
    return await build_claim_context(claim_id)


@pytest.fixture(name='build_claim_context')
def _build_claims_context(build_context_factory, mock_phoenix_traits):
    url = '/internal/cargo-finance/flow/claims/func/claim-billing-context'
    return build_context_factory(url)


@pytest.fixture(name='build_context_factory')
def _build_context_factory(taxi_cargo_finance):
    def wrapper(url):
        async def func(claim_id):
            params = {'claim_id': claim_id}
            response = await taxi_cargo_finance.post(url, params=params)
            assert response.status_code == 200
            return response.json()

        return func

    return wrapper


@pytest.fixture(name='save_claim_context')
def _save_claim_context(save_context_factory):
    url = '/internal/cargo-finance/flow/claims/events/claim-billing-context'
    return save_context_factory(url)


@pytest.fixture(name='save_contractor_context')
def _save_contractor_context(save_context_factory):
    url = (
        '/internal/cargo-finance/flow/claims/events/contractor-billing-context'
    )
    return save_context_factory(url)


@pytest.fixture(name='save_context_factory')
def _save_context_factory(taxi_cargo_finance):
    def wrapper(url):
        async def func(claim_id, context, event_id):
            params = {'claim_id': claim_id}
            data = {'context': context, 'event_id': event_id}
            response = await taxi_cargo_finance.post(
                url, params=params, json=data,
            )
            assert response.status_code == 200
            return response.json()

        return func

    return wrapper


@pytest.fixture(name='set_park_not_found')
def _set_park_not_found(py2_products_response):
    py2_products_response.status = 404


@pytest.fixture(name='filter_py2_products_kinds')
def _filter_py2_products_kinds(request, py2_products_response):
    kinds = request.param or []
    data = py2_products_response.load()
    data['products'] = [
        obj for obj in data['products'] if obj['product'] in kinds
    ]
    py2_products_response.data = data


@pytest.fixture(name='remove_claims_field')
def _remove_claims_field(request, claims_full_response):
    field = request.param
    data = claims_full_response.load()
    del data[field]
    claims_full_response.data = data


@pytest.fixture(name='update_claims_field')
def _update_claims_field(claims_full_response):
    def func(field, new_value):
        data = claims_full_response.load()
        data[field] = new_value
        claims_full_response.data = data

    return func


@pytest.fixture(autouse=True)
def _setup_env(
        mock_procaas_create,
        mock_py2_products,
        mock_py2_fiscal_data,
        mock_claims_full,
        mock_claims_estimated_payment_methods,
        order_proc,
):
    pass
