import pytest

from . import utils_v2


@pytest.fixture(name='create_phoenix_claim')
async def _create_phoenix_claim(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        mock_cargo_corp_up,
):
    async def wrapper():
        headers = get_default_headers()
        headers['X-B2B-Client-Storage'] = 'cargo'
        response = await taxi_cargo_claims.post(
            'api/integration/v2/claims/create',
            params={'request_id': get_default_idempotency_token},
            json=get_create_request_v2(),
            headers=headers,
        )
        return response

    return wrapper


async def test_cannot_erase_phoenix_feature(
        taxi_cargo_claims,
        pgsql,
        get_default_headers,
        get_create_request_v2,
        create_phoenix_claim,
):
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']
    cursor = pgsql['cargo_claims'].cursor()
    # Check feature in PG
    cursor.execute(
        f"""
        SELECT feature_name, is_inner FROM cargo_claims.claim_features
        WHERE claim_uuid = '{claim_id}'
        """,
    )

    feature, is_inner = list(cursor)[0]
    assert feature == 'phoenix_claim'
    assert is_inner is True

    headers = get_default_headers()
    headers['X-B2B-Client-Storage'] = 'cargo'
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': response.json()['version']},
        json=get_create_request_v2(),
        headers=headers,
    )
    assert response.status_code == 200

    cursor.execute(
        f"""
        SELECT feature_name FROM cargo_claims.claim_features
        WHERE claim_uuid = '{claim_id}'
        """,
    )
    assert list(cursor)[0][0] == 'phoenix_claim'


async def test_phoenix_feature_is_not_visible_though_public_api(
        taxi_cargo_claims,
        get_default_headers,
        get_create_request_v2,
        create_phoenix_claim,
):
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim = response.json()
    claim_id = claim['id']
    assert claim['features'] == []

    # edit
    headers = get_default_headers()
    headers['X-B2B-Client-Storage'] = 'cargo'
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': claim['version']},
        json=get_create_request_v2(),
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['features'] == []

    # info
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/info',
        params={'claim_id': claim_id},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['features'] == []

    # search
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=headers,
        json={'offset': 0, 'limit': 5, 'criterias': {'claim_id': claim_id}},
    )
    assert response.status_code == 200
    assert response.json()['claims'][0]['features'] == []


async def test_phoenix_feature_is_visible_though_internal_api(
        taxi_cargo_claims, create_phoenix_claim,
):
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']

    expected_feature = 'phoenix_claim'
    # full
    response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    claim_features = set(feature['id'] for feature in response['features'])
    assert expected_feature in claim_features

    # admin full
    response = await taxi_cargo_claims.post(
        '/v2/admin/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    admin_claim = response.json()['claim']
    claim_features = set(feature['id'] for feature in admin_claim['features'])
    assert expected_feature in claim_features


async def test_phoenix_with_billing_event_feature(
        taxi_cargo_claims, create_phoenix_claim, enable_billing_event_feature,
):
    await enable_billing_event_feature()
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']

    response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)

    claim_features = set(feature['id'] for feature in response['features'])
    expected_features = ['phoenix_claim', 'cargo_finance_billing_event']

    for feature in expected_features:
        assert feature in claim_features


async def test_phoenix_with_using_cargo_pipelines_feature(
        taxi_cargo_claims,
        create_phoenix_claim,
        enable_billing_event_feature,
        enable_using_cargo_pipelines_feature,
):
    await enable_billing_event_feature()
    await enable_using_cargo_pipelines_feature()
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']

    response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)

    claim_features = set(feature['id'] for feature in response['features'])
    expected_features = [
        'phoenix_claim',
        'cargo_finance_billing_event',
        'cargo_finance_use_cargo_pipeline',
    ]

    for feature in expected_features:
        assert feature in claim_features


async def test_phoenix_with_enable_dry_run_for_cargo_pipelines(
        taxi_cargo_claims,
        create_phoenix_claim,
        enable_billing_event_feature,
        enable_using_cargo_pipelines_feature,
        enable_dry_run_in_cargo_pipelines,
):
    await enable_billing_event_feature()
    await enable_using_cargo_pipelines_feature()
    await enable_dry_run_in_cargo_pipelines()
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']

    response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)

    claim_features = set(feature['id'] for feature in response['features'])
    expected_features = [
        'phoenix_claim',
        'cargo_finance_billing_event',
        'cargo_finance_use_cargo_pipeline',
        'cargo_finance_dry_cargo_events',
    ]

    for feature in expected_features:
        assert feature in claim_features


async def test_phoenix_with_use_pricing_dragon_handlers(
        taxi_cargo_claims,
        state_controller,
        enable_use_pricing_dragon_handlers_feature,
        create_phoenix_claim,
):
    response = await create_phoenix_claim()

    assert response.status_code == 200
    claim_id = response.json()['id']

    response = await utils_v2.get_claim(claim_id, taxi_cargo_claims)

    claim_features = set(feature['id'] for feature in response['features'])
    expected_features = ['phoenix_claim', 'use_pricing_dragon_handlers']

    for feature in expected_features:
        assert feature in claim_features
