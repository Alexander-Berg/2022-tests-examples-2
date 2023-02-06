import pytest


CORRECT_REQUESTS = [
    {
        'phone': '+70000000000',
        'details': {
            'external_id': 'external_id',
            'profession': 'test_profession',
        },
        'full_name': {
            'first_name': 'test',
            'last_name': 'test',
            'middle_name': 'test',
        },
        'selfemployed': True,
    },
    {
        'passport_uid': 'passport_uid',
        'details': {
            'external_id': 'external_id',
            'profession': 'test_profession',
        },
        'full_name': {'first_name': 'test', 'last_name': 'test'},
        'selfemployed': True,
    },
]
ERROR_REQUEST_AND_CODE = [
    (
        {
            'details': {
                'external_id': 'external_id',
                'profession': 'test_profession',
            },
            'full_name': {
                'first_name': 'test',
                'last_name': 'test',
                'middle_name': 'test',
            },
            'selfemployed': True,
        },
        'MISSING_PHONE_AND_PASSPORT_UID',
    ),
    (
        {
            'phone': '+70000000000',
            'passport_uid': 'passport_uid',
            'details': {
                'external_id': 'external_id',
                'profession': 'test_profession',
            },
            'full_name': {
                'first_name': 'test',
                'last_name': 'test',
                'middle_name': 'test',
            },
            'selfemployed': True,
        },
        'BOTH_PHONE_AND_PASSPORT_UID',
    ),
]
HEADERS = {
    'X-Idempotency-Token': 'test',
    'X-Platform-Consumer': 'test_consumer',
}

GET_PROFILE_QUERY = """
SELECT park_id, contractor_profile_id, first_name, last_name,
middle_name, profession, platform_consumer, phone_pd_id,
passport_uid, idempotency_token, external_id, selfemployed, status
FROM pro_profiles.profiles
WHERE park_id = '{park_id}'
AND contractor_profile_id = '{contractor_profile_id}'
"""


@pytest.mark.parametrize('draft_request', CORRECT_REQUESTS)
async def test_draft_creation(
        taxi_pro_profiles, mockserver, pgsql, draft_request,
):
    phone = draft_request.get('phone')
    passport_uid = draft_request.get('passport_uid')
    phone_pd_id = 'phone_pd_id' if phone else None

    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock(request):
        data = request.json

        assert phone
        assert data['value'] == phone
        assert data['validate']

        return {'id': phone_pd_id, 'value': data['value']}

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/v1', headers=HEADERS, json=draft_request,
    )

    assert response.status_code == 200
    contractor_id = response.json()['profile_id']
    park_id, contractor_profile_id = contractor_id.split('_')
    cursor = pgsql['pro_profiles'].cursor()
    cursor.execute(
        GET_PROFILE_QUERY.format(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
    )
    row = cursor.fetchone()
    assert row == (
        park_id,
        contractor_profile_id,
        draft_request['full_name']['first_name'],
        draft_request['full_name']['last_name'],
        draft_request['full_name'].get('middle_name'),
        draft_request['details']['profession'],
        HEADERS['X-Platform-Consumer'],
        phone_pd_id,
        passport_uid,
        HEADERS['X-Idempotency-Token'],
        draft_request['details']['external_id'],
        draft_request.get('selfemployed', False),
        'draft',
    )


@pytest.mark.parametrize('draft_request, error_code', ERROR_REQUEST_AND_CODE)
async def test_draft_creation_400(
        taxi_pro_profiles, draft_request, error_code,
):
    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/v1', headers=HEADERS, json=draft_request,
    )

    assert response.status_code == 400
    assert response.json()['code'] == error_code


@pytest.mark.parametrize('draft_request', CORRECT_REQUESTS)
async def test_draft_creation_idempotency(
        taxi_pro_profiles, mockserver, pgsql, draft_request,
):
    phone = draft_request.get('phone')
    passport_uid = draft_request.get('passport_uid')
    phone_pd_id = 'phone_pd_id' if phone else None

    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock(request):
        data = request.json

        assert phone
        assert data['value'] == phone
        assert data['validate']

        return {'id': phone_pd_id, 'value': data['value']}

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/v1', headers=HEADERS, json=draft_request,
    )

    assert response.status_code == 200
    contractor_id = response.json()['profile_id']
    park_id, contractor_profile_id = contractor_id.split('_')
    cursor = pgsql['pro_profiles'].cursor()
    cursor.execute(
        GET_PROFILE_QUERY.format(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
    )
    row = cursor.fetchone()
    assert row == (
        park_id,
        contractor_profile_id,
        draft_request['full_name']['first_name'],
        draft_request['full_name']['last_name'],
        draft_request['full_name'].get('middle_name'),
        draft_request['details']['profession'],
        HEADERS['X-Platform-Consumer'],
        phone_pd_id,
        passport_uid,
        HEADERS['X-Idempotency-Token'],
        draft_request['details']['external_id'],
        draft_request.get('selfemployed', False),
        'draft',
    )

    second_response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/v1', headers=HEADERS, json=draft_request,
    )
    assert second_response.status_code == 200
    second_contractor_id = second_response.json()['profile_id']
    assert contractor_id == second_contractor_id
