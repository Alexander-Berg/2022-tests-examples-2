# pylint: disable=protected-access, redefined-outer-name
import datetime

import pytest

from taxi import config
from taxi.clients import driver_trackstory
from taxi.clients import tvm


@pytest.fixture
def tvm_client(simple_secdist, aiohttp_client, patch, db):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config.Config(db),
        session=aiohttp_client,
    )


@pytest.fixture
async def test_app(test_taxi_app, tvm_client):
    test_taxi_app.driver_trackstory_client = (
        driver_trackstory.DriverTrackstoryClient(
            session=test_taxi_app.session, tvm_client=tvm_client,
        )
    )
    return test_taxi_app


@pytest.mark.parametrize(
    ['request_struct', 'request_json', 'response_json', 'response_struct'],
    [
        pytest.param(
            driver_trackstory.GetTrackRequest(
                'dbid_uuid',
                datetime.datetime(2020, 12, 31, 23, 35, 50),
                datetime.datetime(2021, 12, 31, 23, 35, 50),
                adjust=True,
            ),
            {
                'id': 'dbid_uuid',
                'from_time': '2020-12-31T23:35:50Z',
                'to_time': '2021-12-31T23:35:50Z',
                'adjust': True,
            },
            {
                'id': 'dbid_uuid',
                'track': [
                    {
                        'lat': 55.720542907714844,
                        'lon': 37.45069122314453,
                        'timestamp': 1594837534,
                        'direction': 12.3456789,
                    },
                    {
                        'lat': 55.72353744506836,
                        'lon': 37.45051956176758,
                        'timestamp': 1594837565,
                    },
                ],
            },
            driver_trackstory.GetTrackResponse(
                'dbid_uuid',
                [
                    driver_trackstory.GpsPosition(
                        55.720542907714844,
                        37.45069122314453,
                        datetime.datetime(2020, 7, 15, 18, 25, 34),
                        12.3456789,
                    ),
                    driver_trackstory.GpsPosition(
                        55.72353744506836,
                        37.45051956176758,
                        datetime.datetime(2020, 7, 15, 18, 26, 5),
                        None,
                    ),
                ],
            ),
        ),
    ],
)
async def test_get_track(
        test_app,
        request_struct,
        request_json,
        response_json,
        response_struct,
        mockserver,
):
    @mockserver.json_handler('/driver-trackstory/get_track')
    async def _get_track(request):
        assert request.method == 'POST'
        assert request.json == request_json
        return mockserver.make_response(json=response_json)

    response = await test_app.driver_trackstory_client.get_track(
        request_struct,
    )
    assert _get_track.times_called == 1
    assert response == response_struct
