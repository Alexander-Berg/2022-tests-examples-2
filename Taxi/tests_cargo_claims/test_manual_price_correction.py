import pytest

from . import utils_v2

CARGO_CLAIMS_CORP_BILLING_JOB = {
    'dryrun_on': False,
    'corrections_log_on': True,
    'batches_count': 2,
    'process_corrections_count': -1,
}


async def _set_final_price(claim_id, pgsql, price):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'UPDATE cargo_claims.claims SET final_price = \''
        + price
        + '\' WHERE uuid_id = \''
        + claim_id
        + '\';',
    )


async def _dragon_accepted_claim(state_controller, pgsql):
    claim_info = await state_controller.apply(target_status='new')
    await _set_final_price(claim_info.claim_id, pgsql, '1.0')
    await state_controller.apply(target_status='accepted', fresh_claim=False)
    return claim_info


async def _dragon_c2c_accepted_claim(
        state_controller, get_default_corp_client_id, mock_cargo_finance,
):
    state_controller.use_create_version('v2_cargo_c2c')

    payment_method_id = (
        'cargocorp:' + get_default_corp_client_id + ':balance:456:contract:789'
    )
    payment_type = 'cargocorp'
    mock_cargo_finance.method_id = payment_method_id
    state_controller.set_options(
        payment_type=payment_type, payment_method_id=payment_method_id,
    )
    claim_info = await state_controller.prepare()
    return claim_info


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_manual_correction(
        taxi_cargo_claims,
        state_controller,
        run_corp_billing,
        mockserver,
        pgsql,
):
    claim_info = await _dragon_accepted_claim(state_controller, pgsql)

    await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    request = {
        'claim_id': claim_info.claim_id,
        'source': 'test',
        'sum_to_pay': '123.123',
        'currency': 'RUB',
        'last_known_corrections_count': 11,
        'reason': 'TICKET-123',
        'comment': 'test_comment',
    }
    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 200

    @mockserver.json_handler('/corp-billing/v1/pay-order/cargo')
    async def _v1_pay_order_cargo(request):
        assert 'category' in request.json['claim']
        return mockserver.make_response(
            headers={'X-YaRequestId': 'request_id'},
            json={
                'status': {'code': 'SUCCESS', 'message': 'OK'},
                'transaction_id': '123',
            },
            status=200,
        )

    result = await run_corp_billing()
    assert _v1_pay_order_cargo.times_called == 3
    assert result[claim_info.claim_id] == {
        'accepted': 1,
        'delivered_finish': 2,
    }

    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 409


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_manual_correction_c2c(
        taxi_cargo_claims,
        state_controller,
        run_corp_billing,
        get_default_corp_client_id,
        mock_create_event,
        mockserver,
        mock_cargo_finance,
        mock_cargo_corp_up,
):
    mock_create_event()
    claim_info = await _dragon_c2c_accepted_claim(
        state_controller, get_default_corp_client_id, mock_cargo_finance,
    )

    await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    request = {
        'claim_id': claim_info.claim_id,
        'source': 'test',
        'sum_to_pay': '123.123',
        'currency': 'RUB',
        'last_known_corrections_count': 14,
        'reason': 'TICKET-123',
    }
    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 200

    @mockserver.json_handler('/corp-billing/v1/pay-order/cargo')
    async def _v1_pay_order_cargo(request):
        assert 'category' in request.json['claim']
        assert request.json['claim']['client_id'] == get_default_corp_client_id
        return mockserver.make_response(
            headers={'X-YaRequestId': 'request_id'},
            json={
                'status': {'code': 'SUCCESS', 'message': 'OK'},
                'transaction_id': '123',
            },
            status=200,
        )

    result = await run_corp_billing()
    assert _v1_pay_order_cargo.times_called == 3
    assert result[claim_info.claim_id] == {
        'accepted': 1,
        'delivered_finish': 2,
    }


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
    CARGO_CLAIMS_CORP_CLIENTS_WITH_LOGISTIC_CONTRACTS={'__default__': True},
)
async def test_claims_full(
        taxi_cargo_claims, state_controller, get_default_headers, pgsql,
):
    await _dragon_accepted_claim(state_controller, pgsql)
    claim_info = await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
    )
    assert response.json()['just_client_payment']
    assert response.json()['is_new_logistic_contract']


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_deny_manual_price_correction_when_kind_platform_usage(
        state_finished_platform_usage,
        set_manual_price,
        taxi_cargo_claims,
        sum_to_pay='123.123',
):
    response = await set_manual_price(
        state_finished_platform_usage.claim_info.claim_id, sum_to_pay,
    )
    assert response.status == 400
    assert response.json()['code'] == 'forbidden_for_claim_kind'


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.now('2022-06-01T13:10:00.786Z')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_claim_too_old(
        taxi_cargo_claims,
        state_controller,
        run_corp_billing,
        mockserver,
        pgsql,
):
    claim_info = await _dragon_accepted_claim(state_controller, pgsql)

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""UPDATE cargo_claims.claims
            SET created_ts = \'2022-02-28T13:10:00.786Z\'
            WHERE uuid_id = \'{claim_info.claim_id}\'
        """,
    )

    await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    request = {
        'claim_id': claim_info.claim_id,
        'source': 'test',
        'sum_to_pay': '123.123',
        'currency': 'RUB',
        'last_known_corrections_count': 11,
        'reason': 'TICKET-123',
        'comment': 'test_comment',
    }
    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 400
    assert response.json()['code'] == 'claim_too_old_to_change_price'


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_can_set_price_manyally_when_kind_delivery_service(
        state_finished_delivery_service,
        set_manual_price,
        taxi_cargo_claims,
        sum_to_pay='123.123',
):
    response = await set_manual_price(
        state_finished_delivery_service.claim_info.claim_id, sum_to_pay,
    )
    assert response.status == 200

    # Price changes allowed
    claim = await utils_v2.get_claim(
        state_finished_delivery_service.claim_info.claim_id, taxi_cargo_claims,
    )
    assert claim['pricing']['final_price'] == _apply_vat(sum_to_pay)


@pytest.mark.experiments3(filename='exp3_just_client_payment.json')
@pytest.mark.config(
    CARGO_CLAIMS_CORP_BILLING_JOB=CARGO_CLAIMS_CORP_BILLING_JOB,
)
async def test_can_set_price_manyally_kind_null(
        taxi_cargo_claims,
        state_controller,
        set_manual_price,
        pgsql,
        sum_to_pay='123.222',
):
    await _dragon_accepted_claim(state_controller, pgsql)
    claim_info = await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )

    response = await set_manual_price(claim_info.claim_id, sum_to_pay)
    assert response.status_code == 200

    # Price changes allowed
    claim = await utils_v2.get_claim(claim_info.claim_id, taxi_cargo_claims)
    assert claim['pricing']['final_price'] == _apply_vat(sum_to_pay)


@pytest.fixture(name='state_claim_created')
async def _state_claim_created(
        create_claim_segment_matched_car_taxi_class,
        get_default_corp_client_id,
):
    claim_info, segment_id = await create_claim_segment_matched_car_taxi_class(
        get_default_corp_client_id, taxi_class='courier',
    )

    class State:
        def __init__(self):
            self.claim_info = claim_info
            self.segment_id = segment_id

    return State()


@pytest.fixture(name='state_finished_platform_usage')
async def _state_finished_platform_usage(
        state_claim_created, mark_peformer_found, state_controller,
):
    await mark_peformer_found(state_claim_created.segment_id, 'eda')
    await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    return state_claim_created


@pytest.fixture(name='state_finished_delivery_service')
async def _state_finished_delivery_service(
        state_claim_created, mark_peformer_found, state_controller,
):
    await mark_peformer_found(state_claim_created.segment_id, 'courier')
    await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )
    return state_claim_created


@pytest.fixture(name='mark_peformer_found')
def _mark_peformer_found(
        taxi_cargo_claims,
        build_segment_update_request,
        get_default_corp_client_id,
        create_claim_segment_matched_car_taxi_class,
        taxi_order_id='taxi_order_id_1',
):
    async def wrapper(segment_id, taxi_class):
        # Update performer_info
        update_segment_body = build_segment_update_request(
            segment_id, taxi_order_id, with_performer=True, revision=3,
        )
        update_segment_body['performer_info']['taxi_class'] = taxi_class
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={'segments': [update_segment_body]},
        )
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='set_manual_price')
def _set_manual_price(taxi_cargo_claims):
    async def wrapper(claim_id, sum_to_pay):
        claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
        corrections_count = claim['mpc_corrections_count']
        request = {
            'claim_id': claim_id,
            'source': 'test',
            'sum_to_pay': sum_to_pay,
            'currency': 'RUB',
            'last_known_corrections_count': corrections_count,
            'reason': 'TICKET-123',
            'comment': 'test_comment',
        }
        response = await taxi_cargo_claims.post(
            'v2/claims/manual-price-correction',
            json=request,
            headers={
                'X-Yandex-Login': 'yandex_login',
                'X-Yandex-Uid': 'yandex_uid',
            },
        )
        return response

    return wrapper


def _apply_vat(price: str) -> str:
    vat = 1.2
    return '%.4f' % (float(price) * vat)
