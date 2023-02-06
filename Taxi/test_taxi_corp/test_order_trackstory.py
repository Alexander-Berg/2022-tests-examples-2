import pytest


@pytest.mark.parametrize(
    ['archive_api_response', 'expected_result'],
    [
        pytest.param(
            {
                'order': {'performer': {'uuid': 'uuid', 'db_id': 'dbid'}},
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {'taxi_status': 'transporting'},
                                'c': '2020-07-15T21:25:34.013000',
                            },
                            {
                                'p': {'taxi_status': 'complete'},
                                'c': '2020-07-15T22:00:04.013000',
                            },
                        ],
                    },
                },
            },
            {
                'track': [
                    {
                        'lat': 55.720542907714844,
                        'lon': 37.45069122314453,
                        'timestamp': '2020-07-15T21:25:34+0300',
                    },
                    {
                        'lat': 55.72353744506836,
                        'lon': 37.45051956176758,
                        'timestamp': '2020-07-15T21:26:05+0300',
                    },
                ],
            },
        ),
    ],
)
async def test_happy_path(
        taxi_corp_auth_client,
        patch,
        mockserver,
        archive_api_response,
        expected_result,
):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_search(*args, **kwargs):
        return archive_api_response

    @mockserver.json_handler('/driver-trackstory/get_track')
    async def _get_track(request):
        assert request.json['id'] == 'dbid_uuid'
        return mockserver.make_response(
            json={
                'id': 'dbid_uuid',
                'track': [
                    {
                        'lat': 55.720542907714844,
                        'lon': 37.45069122314453,
                        'timestamp': 1594837534,
                    },
                    {
                        'lat': 55.72353744506836,
                        'lon': 37.45051956176758,
                        'timestamp': 1594837565,
                    },
                ],
            },
        )

    response = await taxi_corp_auth_client.get(
        '/1.0/client/client_id/order/order_id1/trackstory',
    )

    assert response.status == 200
    assert await response.json() == expected_result
