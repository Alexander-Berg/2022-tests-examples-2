# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# root conftest for service shuttle-control
from driver_trackstory.fbs import GpsPosition
from driver_trackstory.fbs import GpsPositionAlternative
from driver_trackstory.fbs import Response
from driver_trackstory.fbs import ResponseForDriver
import flatbuffers
import pytest

pytest_plugins = ['shuttle_control_plugins.pytest_plugins']


def set_gps_position(builder, raw):
    GpsPosition.GpsPositionStart(builder)

    GpsPosition.GpsPositionAddLat(builder, float(raw['lat']))
    GpsPosition.GpsPositionAddLon(builder, float(raw['lon']))
    GpsPosition.GpsPositionAddTimestamp(builder, int(raw['timestamp']))
    if 'accuracy' in raw:
        GpsPosition.GpsPositionAddAccuracy(builder, float(raw['accuracy']))
    if 'speed' in raw:
        GpsPosition.GpsPositionAddSpeed(builder, float(raw['speed']))
    if 'direction' in raw:
        GpsPosition.GpsPositionAddDirection(builder, int(raw['direction']))

    return GpsPosition.GpsPositionEnd(builder)


@pytest.fixture(name='driver_trackstory_v2_shorttracks', autouse=True)
def mock_v2_shorttracks(mockserver):
    def build_response(data):
        builder = flatbuffers.Builder(0)

        responses_for_drivers = []

        for response_for_driver in data['data']:
            driver_id = builder.CreateString(response_for_driver['driver_id'])

            raws = []
            if 'raw' in response_for_driver:
                for raw in response_for_driver['raw']:
                    raws.append(set_gps_position(builder, raw))

            adjusted_arr = []
            if 'adjusted' in response_for_driver:
                for adjusted in response_for_driver['adjusted']:
                    adjusted_arr.append(set_gps_position(builder, adjusted))

            alternatives_arr = []
            if 'alternatives' in response_for_driver:
                for alternatives in response_for_driver['alternatives']:
                    alternatives_arr_ = []
                    if 'alternatives' in alternatives:
                        for alternatives_ in alternatives['alternatives']:
                            alternatives_arr_.append(
                                set_gps_position(builder, alternatives_),
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
            self.data = {'data': []}
            self.throw_exc = False
            self.mock = None

        def set_data(self, data):
            self.data = data

        def set_data_from_positions(self, response):
            self.data = {'data': []}
            for resp in response['results']:
                value = {'driver_id': resp['driver_id']}

                pos = resp['position']
                value['raw'] = [pos]
                value['adjusted'] = [pos]

                self.data['data'].append(value)

        def throw_exception(self):
            self.throw_exc = True

    ctx = Context()

    @mockserver.json_handler('/driver-trackstory/v2/shorttracks')
    def _mock(_):
        nonlocal ctx

        if ctx.throw_exc:
            return mockserver.make_response(status=500)

        assert ctx.data

        return mockserver.make_response(
            status=200,
            content_type='application/x-flatbuffers',
            response=build_response(ctx.data),
        )

    ctx.mock = _mock

    return ctx
