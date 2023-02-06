import pytest


@pytest.mark.parametrize(
    ['masking', 'expected_suffix'], ([['yandex_login'], '_id_pd'], [[], '']),
)
async def test_masking_yandex_login(
        taxi_config,
        taxi_cargo_claims,
        get_default_headers,
        create_claim_for_segment,
        masking,
        expected_suffix,
        pgsql,
):
    taxi_config.set_values(
        {'CARGO_CLAIMS_PERSONAL_DATA_MASKING': {'masking': masking}},
    )
    claim_id = (await create_claim_for_segment()).claim_id

    # step 1. the data was saved with masking
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute('SELECT yandex_login FROM cargo_claims.claims')
    assert list(cursor) == [('abacaba' + expected_suffix,)]

    # step 2. topics should give personal data with masking if exist
    topics_with_masking_data = [
        ('/v2/claims/full', 'get'),
        ('/v2/admin/claims/full', 'post'),
    ]
    for topic, method in topics_with_masking_data:
        response = await getattr(taxi_cargo_claims, method)(
            topic, params={'claim_id': claim_id},
        )
        assert response.status_code == 200

        json = response.json()
        json = json if 'claim' not in json else json['claim']
        if masking:
            assert 'initiator_yandex_login' not in json
            assert json['personal_initiator_yandex_login_id'] == 'abacaba_id'
        else:
            assert 'personal_initiator_yandex_login_id' not in json
            assert json['initiator_yandex_login'] == 'abacaba'

    # step 3. /api/integration/* should give personal data without masking
    topics_without_masking_data = (
        ('/api/integration/v2/claims/info', {}),
        ('/api/integration/v2/claims/search', {'offset': 0, 'limit': 1}),
        ('/api/integration/v2/claims/bulk_info', {'claim_ids': [claim_id]}),
    )
    for method, json in topics_without_masking_data:
        response = await taxi_cargo_claims.post(
            method,
            headers=get_default_headers(),
            params={'claim_id': claim_id},
            json=json,
        )
        assert response.status_code == 200

        json = response.json()
        json = json if 'claims' not in json else json['claims'][0]

        assert json['initiator_yandex_login'] == 'abacaba'
