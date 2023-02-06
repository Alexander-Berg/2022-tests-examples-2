import pytest


ALL_WITH_PASSPORT = [
    {
        'driver_id': 'driver_id',
        'park_id': 'park_id_1',
        'profession': 'scooter',
        'status': 'processing',
        'city': 'Москва',
    },
    {
        'driver_id': 'driver_id',
        'park_id': 'park_id_2',
        'profession': 'moto',
        'status': 'draft',
        'city': 'Москва',
    },
]


@pytest.mark.pgsql('pro_profiles', files=['profiles.sql'])
@pytest.mark.parametrize(
    'request_body, expected_profiles',
    [
        pytest.param(
            {'passport_uid': 'passport_uid'}, ALL_WITH_PASSPORT, id='passport',
        ),
        pytest.param(
            {'passport_uid': 'passport_uid', 'status': 'processing'},
            ALL_WITH_PASSPORT[:1],
            id='passport+status',
        ),
        pytest.param(
            {'passport_uid': 'passport_uid_wrong'}, [], id='no_such_passport',
        ),
        pytest.param(
            {'passport_uid': 'passport_uid', 'status': 'failed'},
            [],
            id='no_such_status',
        ),
    ],
)
async def test_find(taxi_pro_profiles, request_body, expected_profiles):

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/find-by-passport-uid/v1',
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == {'profiles': expected_profiles}
