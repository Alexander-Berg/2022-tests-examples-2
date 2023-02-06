import pytest

from . import utils_v2

CORP_CLIENT_ID = '01234567890123456789012345678912'


@pytest.fixture(name='create_claim_with_storage')
async def _create_claim_with_storage(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
):
    async def wrapper(storage):
        headers = get_default_headers()
        if storage:
            headers['X-B2B-Client-Storage'] = storage
        response = await taxi_cargo_claims.post(
            'api/integration/v2/claims/create',
            params={'request_id': get_default_idempotency_token},
            json=get_create_request_v2(),
            headers=headers,
        )
        return response

    return wrapper


@pytest.fixture(name='check_features')
def _check_features(taxi_cargo_claims):
    async def _wrapper(
            claim_id, expected_features=None, missing_features=None,
    ):
        if expected_features is None:
            expected_features = {}
        if missing_features is None:
            missing_features = {}
        response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
        claim_features = set(feature['id'] for feature in response['features'])
        for expected_feature in expected_features:
            assert expected_feature in claim_features
        for missing_feature in missing_features:
            assert missing_feature not in claim_features

    return _wrapper


async def test_created_by_old_corp(
        mock_cargo_corp_up, create_claim_with_storage, check_features,
):
    response = await create_claim_with_storage(storage='taxi')
    assert response.status_code == 200
    claim_id = response.json()['id']

    missing_features = {
        'phoenix_claim',
        'agent_scheme',
        'phoenix_corp',
        'c2c_interface',
    }
    assert mock_cargo_corp_up.handler_client_traits.times_called == 0
    await check_features(claim_id, missing_features=missing_features)


@pytest.mark.experiments3(
    filename='config_force_check_small_business_trait.json',
)
async def test_created_by_old_corp_force_check_enabled(
        mock_cargo_corp_up, create_claim_with_storage, check_features,
):
    mock_cargo_corp_up.is_agent_scheme = False
    response = await create_claim_with_storage(storage='taxi')
    assert response.status_code == 200
    claim_id = response.json()['id']

    missing_features = {
        'phoenix_claim',
        'agent_scheme',
        'phoenix_corp',
        'c2c_interface',
    }
    assert mock_cargo_corp_up.handler_client_traits.times_called == 1
    await check_features(claim_id, missing_features=missing_features)


@pytest.mark.parametrize('with_card', [True, False])
async def test_created_by_new_corp(
        mock_cargo_corp_up,
        create_claim_with_storage,
        check_features,
        with_card,
):
    mock_cargo_corp_up.is_agent_scheme = with_card
    response = await create_claim_with_storage(storage='cargo')
    assert response.status_code == 200
    claim_id = response.json()['id']

    missing_features = {'c2c_interface'}
    expected_features = {'phoenix_corp'}
    if with_card:
        expected_features.update({'phoenix_claim', 'agent_scheme'})
    else:
        missing_features.update({'phoenix_claim', 'agent_scheme'})
    assert mock_cargo_corp_up.handler_client_traits.times_called == 1
    await check_features(
        claim_id,
        expected_features=expected_features,
        missing_features=missing_features,
    )


@pytest.mark.parametrize('storage', ['taxi', 'cargo'])
@pytest.mark.experiments3(
    filename='config_force_check_small_business_trait.json',
)
async def test_cargo_corp_is_down(
        create_claim_with_storage, mock_cargo_corp, storage,
):
    """Feature should be set by cargo-corp, but it is down"""

    mock_cargo_corp.is_cargo_corp_down = True

    response = await create_claim_with_storage(storage=storage)
    assert response.status_code == 500

    assert mock_cargo_corp.handler_client_traits.times_called == 1


async def test_new_corp_v1_create(
        claim_creator, mock_cargo_corp_up, get_default_headers, check_features,
):
    headers = get_default_headers()
    headers['X-B2B-Client-Storage'] = 'cargo'
    response = await claim_creator(headers=headers)
    assert response.status_code == 200
    claim_id = response.json()['id']

    expected_features = {'phoenix_claim', 'agent_scheme', 'phoenix_corp'}
    missing_features = {'c2c_interface'}

    assert mock_cargo_corp_up.handler_client_traits.times_called == 1
    await check_features(
        claim_id,
        expected_features=expected_features,
        missing_features=missing_features,
    )


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_verify_corp_id_create_accepted',
    consumers=['cargo-claims/estimation_result'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'value': 'grocery',
                    'arg_name': 'employer_name',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'is_allowed': True},
        },
    ],
    default_value={'is_allowed': False},
    is_config=True,
)
async def test_new_corp_create_accepted(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        get_v2_estimation_result,
        mock_cargo_corp_up,
        check_features,
):
    mock_cargo_corp_up.is_agent_scheme = False
    request_id = get_default_idempotency_token
    request_v2 = get_create_request_v2()
    request = {
        'claim': request_v2,
        'estimation_result': get_v2_estimation_result,
        'client': {'corp_client_id': CORP_CLIENT_ID},
    }
    headers = get_default_headers()
    headers['X-B2B-Client-Storage'] = 'cargo'
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create-accepted?request_id={request_id}',
        json=request,
        headers=headers,
    )
    assert response.status_code == 200
    claim_id = response.json()['id']

    expected_features = {'phoenix_corp'}
    missing_features = {'c2c_interface', 'phoenix_claim', 'agent_scheme'}

    assert mock_cargo_corp_up.handler_client_traits.times_called == 1
    await check_features(
        claim_id,
        expected_features=expected_features,
        missing_features=missing_features,
    )
