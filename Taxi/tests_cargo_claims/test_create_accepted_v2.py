import copy


import pytest

OFFER_ID = 'taxi_offer_id_1'
CORP_CLIENT_ID = '01234567890123456789012345678912'


@pytest.fixture(name='get_default_headers_none_auth')
def _get_default_headers_none_auth(get_default_headers):
    result = get_default_headers()
    result.pop('X-B2B-Client-Id')
    return result


@pytest.fixture(name='v2_create_accepted')
def _v2_create_accepted(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_idempotency_token,
        get_default_headers_none_auth,
        get_default_corp_client_id,
        get_v2_estimation_result,
):
    class Context:
        request = {
            'claim': get_create_request_v2(),
            'estimation_result': get_v2_estimation_result,
            'client': {'corp_client_id': get_default_corp_client_id},
        }

        async def call(self, extra_requirement=None, zone_id=None):
            request = copy.deepcopy(self.request)
            print(request['claim'])

            if zone_id is not None:
                request['claim']['route_points'][0]['address'][
                    'coordinates'
                ] = (
                    [27.561831, 53.902284]
                )  # minsk
                request['estimation_result']['trip']['zone_id'] = zone_id
                request['claim']['c2c_data'] = {'payment_type': 'card'}
            if extra_requirement is not None:
                request['estimation_result']['vehicle']['taxi_requirements'][
                    'extra_requirement'
                ] = extra_requirement
            return await taxi_cargo_claims.post(
                '/v2/claims/create-accepted',
                headers=get_default_headers_none_auth,
                params={'request_id': get_default_idempotency_token},
                json=request,
            )

    return Context()


@pytest.fixture(name='get_full_claim')
async def _get_full_claim(taxi_cargo_claims, get_default_headers):
    async def _wrapper(claim_id):
        response = await taxi_cargo_claims.get(
            '/v2/claims/full',
            headers=get_default_headers(),
            params={'claim_id': claim_id},
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='exp3_verify_corp_id_create_accepted')
async def _exp3_verify_corp_id_create_accepted(experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_verify_corp_id_create_accepted',
        consumers=['cargo-claims/estimation_result'],
        clauses=[],
        default_value={'is_allowed': True},
    )


def _check_searched_claim_data(claim, corp_client_id):
    assert claim['corp_client_id'] == corp_client_id

    assert claim['status'] == 'accepted'
    assert claim['matched_cars'] == [
        {'door_to_door': True, 'taxi_class': 'express'},
    ]


def _check_full_claim_data(claim, corp_client_id):
    _check_searched_claim_data(claim, corp_client_id)
    assert claim['dispatch_flow'] == 'newway'
    assert claim['taxi_offer']['offer_id'] == OFFER_ID
    assert claim['taxi_requirements'] == {'door_to_door': True}

    assert claim['pricing']['offer']['price'] == '1198.8012'
    assert not claim['is_delayed']


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_create_v2_claim_accepted(
        v2_create_accepted,
        get_full_claim,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    create_response = await v2_create_accepted.call()
    assert create_response.status_code == 200
    _check_searched_claim_data(
        create_response.json(), get_default_corp_client_id,
    )
    claim_id = create_response.json()['id']

    claim = await get_full_claim(claim_id)
    _check_full_claim_data(claim, get_default_corp_client_id)


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_create_v2_claim_accepted_bad_receipt_zone(
        v2_create_accepted,
        get_full_claim,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    create_response = await v2_create_accepted.call(zone_id='minsk')
    assert create_response.status_code == 400


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.config(
    CARGO_CLAIMS_REQUIREMENTS_TO_SPECIAL_REQUIREMENT_LISTS_MAP={
        'cargo': {'extra_requirement': ['extra_requirement_spec1']},
    },
)
async def test_create_v2_claim_accepted_with_extra_requirement(
        v2_create_accepted,
        get_full_claim,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
        taxi_cargo_claims,
):
    create_response = await v2_create_accepted.call(extra_requirement=17)
    assert create_response.status_code == 200
    # требования из estimate_result в ответах нигде не торчат
    # поэтому проверяем по косвенным признакам
    # через маппинг на спецтребования
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_response.json()['id'],
        },
    )
    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        {
            'class': 'cargo',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'cargo_multipoints'},
                {'id': 'extra_requirement_spec1'},
            ],
        },
        {
            'class': 'express',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'cargo_multipoints'},
            ],
        },
    ]


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_accept_only(
        get_full_claim,
        state_controller,
        v2_create_accepted,
        exp3_verify_corp_id_create_accepted,
):
    # моделируем ситуацию повторного вызова ручки,
    # когда в первом вызове заявка создалась, но не была принята
    # для этого создаем заявку другой ручкой
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id

    create_response = await v2_create_accepted.call()
    assert create_response.status_code == 200
    assert claim_id == create_response.json()['id']

    claim = await get_full_claim(claim_id)
    assert claim['status'] == 'accepted'


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_create_v2_claim_accepted_processing(
        v2_create_accepted,
        query_processing_events,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    create_response = await v2_create_accepted.call()
    assert create_response.status_code == 200

    claim_id = create_response.json()['id']
    event = query_processing_events(claim_id)[1]
    assert event.payload['data'].pop('claim_revision') > 0
    assert event.payload == {
        'data': {
            'calc_id': 'taxi_offer_id_1',
            'total_price': '999.001',
            'phoenix_claim': False,
        },
        'kind': 'price-changed',
        'status': 'ready_for_approval',
    }


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_create_v2_claim_accepted_idempotancy(
        v2_create_accepted,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    create_response1 = await v2_create_accepted.call()
    assert create_response1.status_code == 200

    create_response2 = await v2_create_accepted.call()
    assert create_response2.status_code == 200

    assert create_response1.json()['id'] == create_response2.json()['id']


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
async def test_create_v2_claim_accepted_without_estimation_result(
        v2_create_accepted,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    create_accepted = v2_create_accepted
    del create_accepted.request['estimation_result']
    response = await create_accepted.call()
    assert response.status_code == 400
    assert response.json() == {
        'message': 'estimation_result was not found.',
        'code': 'validation_error',
    }


async def test_no_corp_validation(
        v2_create_accepted,
        get_default_corp_client_id,
        exp3_verify_corp_id_create_accepted,
):
    create_response1 = await v2_create_accepted.call()
    assert create_response1.status_code == 200
