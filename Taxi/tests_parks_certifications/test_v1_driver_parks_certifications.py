import pytest

AUTH_PARAMS = {'park_id': 'db_id1'}

HEADERS = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-Driver-Session': 'session1',
}


@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        (
            {'park_ids': ['db_id1']},
            {'certifications': [{'park_id': 'db_id1', 'is_certified': True}]},
        ),
        (
            {'park_ids': ['db_id1', 'db_id2']},
            {
                'certifications': [
                    {'park_id': 'db_id1', 'is_certified': True},
                    {'park_id': 'db_id2', 'is_certified': False},
                ],
            },
        ),
        (
            {'park_ids': ['db_id3']},
            {'certifications': [{'park_id': 'db_id3', 'is_certified': False}]},
        ),
    ],
)
async def test_certifications_ok(
        taxi_parks_certifications,
        request_body,
        expected_response,
        driver_authorizer,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_parks_certifications.post(
        '/v1/driver/parks/certifications/list',
        params=AUTH_PARAMS,
        headers=HEADERS,
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
