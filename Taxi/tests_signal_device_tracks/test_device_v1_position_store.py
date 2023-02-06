# pylint: disable=import-error
import flatbuffers
import pytest
from signal_device_tracks.positions.fbs import V1CameraPosition
from signal_device_tracks.positions.fbs import V1CameraPositions


ENDPOINT = '/signal-device/v1/signal-device-tracks/device/v1/position/store'

POSITIONS = [
    {
        'lat': 1.0,
        'lon': 1.0,
        'unix_timestamp': 1,
        'accuracy': 2.0,
        'altitude': 2,
        'direction': 1,
        'speed': 4,
    },
    {
        'lat': 2.0,
        'lon': 2.0,
        'unix_timestamp': 2,
        'accuracy': 2.0,
        'altitude': 2,
        'direction': 1,
        'speed': 4,
    },
]


POSITIONS2 = [
    {
        'lat': 1.0,
        'lon': 1.0,
        'unix_timestamp': 1,
        'accuracy': 2.0,
        'altitude': 2,
        'direction': 1.0,
        'speed': 4,
    },
    {
        'lat': 2.0,
        'lon': 2.0,
        'unix_timestamp': 2,
        'accuracy': 2.0,
        'altitude': 2,
        'direction': 1.0,
        'speed': 4,
    },
]


@pytest.mark.config(CAMERA_USE_PIPELINE_YAGR=True)
@pytest.mark.parametrize(
    'fbs_schema_version, positions',
    [(None, POSITIONS), ('v1', POSITIONS), ('v2', POSITIONS2)],
)
async def test_position_store(
        taxi_signal_device_tracks, mockserver, fbs_schema_version, positions,
):
    @mockserver.json_handler('/yagr/camera/position/v2/store')
    def _register_device_camera(request):
        for position in request.json['positions']:
            assert position['contractor_uuid'] == '123'
            assert position['contractor_dbid'] == 'p1'
            assert position['source'] == 'Camera'

            position.pop('contractor_uuid')
            position.pop('contractor_dbid')
            position.pop('source')

        assert len(request.json['positions']) == len(positions)

        return mockserver.make_response(
            json={}, headers={'X-Polling-Power-Policy': 'lol'}, status=200,
        )

    @mockserver.json_handler('/yagr/pipeline/camera/position/store')
    def _register_device_pipeline(request):
        for position in request.json['positions']:
            assert position['contractor_uuid'] == '123'
            assert position['contractor_dbid'] == 'p1'
            assert position['source'] == 'Verified'

        assert len(request.json['positions']) == len(positions)
        return mockserver.make_response(json={}, headers={}, status=200)

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def _register_device_fts(request):
        assert request.args['uuid'] == 'p1_123'
        assert request.args['pipeline'] == 'camera'
        assert request.headers['X-YaFts-Client-Service-Tvm'] == '0'
        assert len(request.json['positions']) == 1

        return mockserver.make_response(json={}, status=200)

    builder = flatbuffers.Builder(0)
    fbs_positions = [
        V1CameraPosition.CreateV1CameraPosition(
            builder,
            position['lat'],
            position['lon'],
            position['unix_timestamp'],
            position['accuracy'],
            position['altitude'],
            position['speed'],
            position['direction'],
        )
        for position in positions
    ]
    fbs_positions.reverse()
    V1CameraPositions.V1CameraPositionsStartPositionsVector(
        builder, len(fbs_positions),
    )
    for fbs_position in fbs_positions:
        builder.PrependUOffsetTRelative(fbs_position)
    fbs_positions = builder.EndVector(len(fbs_positions))

    V1CameraPositions.V1CameraPositionsStart(builder)
    V1CameraPositions.V1CameraPositionsAddPositions(builder, fbs_positions)
    request_fbs = V1CameraPositions.V1CameraPositionsEnd(builder)
    builder.Finish(request_fbs)

    params = {'park_id': 'p1', 'serial_number': '123'}
    if fbs_schema_version is not None:
        params['fbs_schema_version'] = fbs_schema_version

    # TODO: сделать тесты с нормальным заполнением flatbuff-а (отдельный ПР)
    response = await taxi_signal_device_tracks.post(
        ENDPOINT,
        params=params,
        headers={'Content-Type': 'application/flatbuffer'},
        data=builder.Output(),
    )
    assert response.status_code == 200, response.text

    assert _register_device_fts.times_called == len(positions)
