# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_trackstory.fbs import GpsPosition
from driver_trackstory.fbs import GpsPositionAlternative
from driver_trackstory.fbs import Response
from driver_trackstory.fbs import ResponseForDriver
import flatbuffers
import pytest
from reposition_watcher_plugins import *  # noqa: F403 F401


# Since TVM grants access to all used services,
# calls to /maps-router/v2/summary must be mocked explicitly
@pytest.fixture
def mock_maps_router(mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _handler(request):
        return mockserver.make_response(status=500)


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.fixture(name='driver_trackstory_v2_shorttracks')
def mock_v2_shorttracks(mockserver):
    def build_response(data):
        builder = flatbuffers.Builder(0)

        responses_for_drivers = []

        for response_for_driver in data['data']:
            driver_id = builder.CreateString(response_for_driver['driver_id'])

            raws = []
            if 'raw' in response_for_driver:
                for raw in response_for_driver['raw']:
                    lat = float(raw['lat'])
                    lon = float(raw['lon'])
                    timestamp = int(raw['timestamp'])
                    accuracy = float(raw['accuracy'])
                    speed = float(raw['speed'])
                    direction = int(raw['direction'])

                    GpsPosition.GpsPositionStart(builder)

                    GpsPosition.GpsPositionAddLat(builder, lat)
                    GpsPosition.GpsPositionAddLon(builder, lon)
                    GpsPosition.GpsPositionAddTimestamp(builder, timestamp)
                    GpsPosition.GpsPositionAddAccuracy(builder, accuracy)
                    GpsPosition.GpsPositionAddSpeed(builder, speed)
                    GpsPosition.GpsPositionAddDirection(builder, direction)

                    raws.append(GpsPosition.GpsPositionEnd(builder))

            adjusted_arr = []
            if 'adjusted' in response_for_driver:
                for adjusted in response_for_driver['adjusted']:
                    lat = float(adjusted['lat'])
                    lon = float(adjusted['lon'])
                    timestamp = int(adjusted['timestamp'])
                    accuracy = float(adjusted['accuracy'])
                    speed = float(adjusted['speed'])
                    direction = int(adjusted['direction'])

                    GpsPosition.GpsPositionStart(builder)

                    GpsPosition.GpsPositionAddLat(builder, lat)
                    GpsPosition.GpsPositionAddLon(builder, lon)
                    GpsPosition.GpsPositionAddTimestamp(builder, timestamp)
                    GpsPosition.GpsPositionAddAccuracy(builder, accuracy)
                    GpsPosition.GpsPositionAddSpeed(builder, speed)
                    GpsPosition.GpsPositionAddDirection(builder, direction)

                    adjusted_arr.append(GpsPosition.GpsPositionEnd(builder))

            alternatives_arr = []
            if 'alternatives' in response_for_driver:
                for alternatives in response_for_driver['alternatives']:
                    alternatives_arr_ = []
                    if 'alternatives' in alternatives:
                        for alternatives_ in alternatives['alternatives']:
                            lat = float(alternatives_['lat'])
                            lon = float(alternatives_['lon'])
                            timestamp = int(alternatives_['timestamp'])
                            accuracy = float(alternatives_['accuracy'])
                            speed = float(alternatives_['speed'])
                            direction = int(alternatives_['direction'])

                            GpsPosition.GpsPositionStart(builder)

                            GpsPosition.GpsPositionAddLat(builder, lat)
                            GpsPosition.GpsPositionAddLon(builder, lon)
                            GpsPosition.GpsPositionAddTimestamp(
                                builder, timestamp,
                            )
                            GpsPosition.GpsPositionAddAccuracy(
                                builder, accuracy,
                            )
                            GpsPosition.GpsPositionAddSpeed(builder, speed)
                            GpsPosition.GpsPositionAddDirection(
                                builder, direction,
                            )

                            alternatives_arr_.append(
                                GpsPosition.GpsPositionEnd(builder),
                            )

                    GpsPositionAlternative.GpsPositionAlternativeStartAlternativesVector(  # noqa: E501
                        builder, len(alternatives_arr_),
                    )
                    for alternatives_ in reversed(alternatives_arr_):
                        builder.PrependUOffsetTRelative(alternatives_)
                    alternatives_arr_ = builder.EndVector(
                        len(alternatives_arr_),
                    )

                    GpsPositionAlternative.GpsPositionAlternativeStart(builder)
                    GpsPositionAlternative.GpsPositionAlternativeAddAlternatives(  # noqa: E501
                        builder, alternatives_arr_,
                    )
                    alternatives_arr.append(
                        GpsPositionAlternative.GpsPositionAlternativeEnd(
                            builder,
                        ),
                    )

            if raws:
                ResponseForDriver.ResponseForDriverStartRawVector(
                    builder, len(raws),
                )
                for raw in reversed(raws):
                    builder.PrependUOffsetTRelative(raw)
                raws = builder.EndVector(len(raws))

            if adjusted_arr:
                ResponseForDriver.ResponseForDriverStartAdjustedVector(
                    builder, len(adjusted_arr),
                )
                for adjusted in reversed(adjusted_arr):
                    builder.PrependUOffsetTRelative(adjusted)
                adjusted_arr = builder.EndVector(len(adjusted_arr))

            if alternatives_arr:
                ResponseForDriver.ResponseForDriverStartAlternativesVector(
                    builder, len(alternatives_arr),
                )
                for alternatives in reversed(alternatives_arr):
                    builder.PrependUOffsetTRelative(alternatives)
                alternatives_arr = builder.EndVector(len(alternatives_arr))

            ResponseForDriver.ResponseForDriverStart(builder)
            ResponseForDriver.ResponseForDriverAddDriverId(builder, driver_id)
            if raws:
                ResponseForDriver.ResponseForDriverAddRaw(builder, raws)
            if adjusted_arr:
                ResponseForDriver.ResponseForDriverAddAdjusted(
                    builder, adjusted_arr,
                )
            if alternatives_arr:
                ResponseForDriver.ResponseForDriverAddAlternatives(
                    builder, alternatives_arr,
                )
            responses_for_drivers.append(
                ResponseForDriver.ResponseForDriverEnd(builder),
            )

        Response.ResponseStartDataVector(builder, len(responses_for_drivers))
        for response_for_driver in reversed(responses_for_drivers):
            builder.PrependUOffsetTRelative(response_for_driver)
        responses_for_drivers = builder.EndVector(len(responses_for_drivers))

        Response.ResponseStart(builder)
        Response.ResponseAddData(builder, responses_for_drivers)
        response = Response.ResponseEnd(builder)

        builder.Finish(response)

        return builder.Output()

    class Context:
        def __init__(self):
            self.data = {}
            self.mock = None

        def set_data(self, data):
            self.data = data

    ctx = Context()

    @mockserver.json_handler('/driver-trackstory/v2/shorttracks')
    def _mock(_):
        nonlocal ctx

        assert ctx.data

        return mockserver.make_response(
            status=200,
            content_type='application/x-flatbuffers',
            response=build_response(ctx.data),
        )

    ctx.mock = _mock

    return ctx
