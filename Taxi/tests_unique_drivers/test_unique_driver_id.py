import pytest


@pytest.mark.parametrize(
    'db,uuid,consumer,expected_code,parks_response,expected_response',
    [
        (
            'db_01',
            'uuid_01',
            'testsuite',
            200,
            {
                'driver_profiles': [
                    {
                        'driver_profile': {
                            'license': {'normalized_number': 'LICENSE_001'},
                        },
                    },
                ],
            },
            {'unique_driver_id': '000000000000000000000001'},
        ),
        ('db_01', 'uuid_01', 'testsuite', 502, {}, {}),
        (
            'db_01',
            'uuid_01',
            'testsuite',
            502,
            {'driver_profiles': [{'driver_profile': {}}]},
            {},
        ),
        (
            'db_bad',
            'uuid_bad',
            'testsuite',
            404,
            {
                'driver_profiles': [
                    {
                        'driver_profile': {
                            'license': {'normalized_number': 'license_bad'},
                        },
                    },
                ],
            },
            {},
        ),
        ('db_01', 'uuid_01', 'testsuite-bad', 404, {}, {}),
    ],
)
@pytest.mark.now('2019-03-10T00:00:00')
@pytest.mark.config(
    TVM_ENABLED=False, CONSUMERS_WHITE_LIST={'unique-drivers': ['testsuite']},
)
async def test_driver_unique_driver_id(
        taxi_unique_drivers,
        mockserver,
        db,
        uuid,
        consumer,
        expected_code,
        parks_response,
        expected_response,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == {
            'query': {'park': {'driver_profile': {'id': [uuid]}, 'id': db}},
            'fields': {'driver_profile': ['license']},
        }
        return parks_response

    response = await taxi_unique_drivers.get(
        'v1/driver/unique_driver_id',
        params={'db': db, 'uuid': uuid, 'consumer': consumer},
    )

    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        # don't check error message textual representation
        assert response.json() == expected_response
