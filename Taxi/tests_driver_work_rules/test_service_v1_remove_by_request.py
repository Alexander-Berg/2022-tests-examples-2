import pytest

from tests_driver_work_rules import defaults


ENDPOINT = 'service/v1/change-logger/remove-by-request'


@pytest.mark.pgsql('misc', files=['changes.sql'])
@pytest.mark.parametrize(
    'request_body',
    [
        {
            'park_id': 'extra_super_park_id_1',
            'object_id': 'extra_super_object_id_2',
            'object_type': 'TaxiServer.Models.Driver.Driver',
        },
    ],
)
async def test_ok(
        taxi_driver_work_rules, fleet_parks_shard, pgsql, request_body,
):
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=defaults.HEADERS,
        json=request_body,
        params={'consumer': 'service_name'},
    )
    assert response.status_code == 200
    cursor = pgsql['misc'].cursor()
    cursor.execute('SELECT * FROM changes_0 ')

    left_rows = cursor.fetchall()

    assert left_rows != 0

    for entry in left_rows:
        assert entry[0] != request_body['park_id']
        assert entry[3] != request_body['object_id']
