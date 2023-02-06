# pylint: disable=import-error,too-many-lines,import-only-modules
import pytest


MOCK_NOW = '2020-09-14T14:15:16+0000'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_main(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.623760,
                        'lat': 55.749887,
                        'timestamp': 1600092910,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.623764,
                        'lat': 55.749887,
                        'timestamp': 1600092910,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    # Dummy /v2/route mock
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    request_json = {'subvention_geoarea': 'msk_shuttle_subv'}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/subventions/list-drivers-in-geoarea',
        json=request_json,
    )

    assert (
        sorted(
            response.json()['drivers'], key=lambda x: x['driver_profile_id'],
        )
        == sorted(
            [
                {
                    'park_id': 'dbid0',
                    'driver_profile_id': 'uuid0',
                    'shuttle_descriptor': {
                        'shuttle_id': 'gkZxnYQ73QGqrKyz',
                        'started_at': '2020-09-14T12:15:16+00:00',
                    },
                    'shuttle_state': {
                        'position': [37.62376, 55.749887],
                        'status': 'active',
                    },
                },
                {
                    'park_id': 'dbid1',
                    'driver_profile_id': 'uuid1',
                    'shuttle_descriptor': {
                        'shuttle_id': 'Pmp80rQ23L4wZYxd',
                        'started_at': '2020-09-14T12:15:16+00:00',
                    },
                    'shuttle_state': {
                        'position': [37.623764, 55.749887],
                        'status': 'blocked',
                        'block_reason': 'not_en_route',
                    },
                },
            ],
            key=lambda x: x['driver_profile_id'],
        )
    )
