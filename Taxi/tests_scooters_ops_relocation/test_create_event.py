import pytest

from tests_scooters_ops_relocation import utils


HANDLER = '/scooters-ops-relocation/v1/events/create'


@pytest.mark.parametrize(
    'request_version,event_version',
    [
        pytest.param(None, 1, id='no version in request'),
        pytest.param(11, 11, id='some version in request'),
    ],
)
async def test_create_order_completed_event(
        taxi_scooters_ops_relocation, pgsql, request_version, event_version,
):
    payload = {
        'type': 'order-completed',
        'payload': {
            'point_start': {'lon': 35, 'lat': 52},
            'point_end': {'lon': 35, 'lat': 53},
            'started_at': '2021-01-01T10:25:11+0300',
            'ended_at': '2021-01-01T11:25:11+0300',
            'vehicle_id': 'vehicle_id_0',
        },
    }

    if request_version is not None:
        payload['version'] = request_version

    resp = await taxi_scooters_ops_relocation.post(
        HANDLER, payload, headers={'X-Idempotency-Token': 'event1'},
    )

    assert resp.status_code == 200, resp.text
    assert utils.get_events(pgsql) == [
        {
            'id': 'event1_income',
            'type': 'income',
            'polygon_id': None,
            'occured_at': utils.parse_timestring_aware(
                '2021-01-01T11:25:11+0300',
            ),
            'extra': {'vehicle_id': 'vehicle_id_0'},
            'location': '(35,53)',
            'iteration': None,
            'region': None,
            'version': event_version,
        },
        {
            'id': 'event1_outcome',
            'type': 'outcome',
            'polygon_id': None,
            'occured_at': utils.parse_timestring_aware(
                '2021-01-01T10:25:11+0300',
            ),
            'extra': {'vehicle_id': 'vehicle_id_0'},
            'location': '(35,52)',
            'iteration': None,
            'region': None,
            'version': event_version,
        },
    ]
