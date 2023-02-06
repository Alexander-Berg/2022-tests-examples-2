import gzip

import flatbuffers
# pylint: disable=import-error
from handlers.frozen import FrozenDrivers
import pytest


_FROZEN_MARKER = 'frozen_drivers'
_SERVICE = '/driver-freeze'
# Usage: @pytest.mark.frozen_drivers(
#            frozen_drivers={
#                'unique_driver_ids': ['udid0', ...],
#                'car_ids': ['LX123A78', ...],
#                'timestamp': 123,
#             }
#        )
_FROZEN_URL = '/frozen'


class FrozenDriversContext:
    def __init__(self):
        self.response_fbs = None
        self.errors = {}
        self.calls = {}

    def reset(self):
        self.response_fbs = None
        self.errors = {}
        self.calls = {}

    def set_frozen_drivers_fbs(self, frozen_drivers_fbs):
        self.response_fbs = frozen_drivers_fbs

    def set_frozen_drivers(self, frozen_drivers):
        self.response_fbs = self.build_frozen_drivers(frozen_drivers)

    def set_error(self, handler, error_code, error_message=None):
        self.errors[handler] = {
            'code': error_code,
            'message': error_message or 'Server error',
        }

    def build_frozen_drivers(self, frozen_drivers):
        builder = flatbuffers.Builder(0)

        # pack unique_driver_ids
        fbs_udids = [
            builder.CreateString(udid)
            for udid in frozen_drivers['unique_driver_ids']
        ]
        FrozenDrivers.FrozenDriversStartUniqueDriverIdsVector(
            builder, len(fbs_udids),
        )
        for fbs_udid in fbs_udids:
            builder.PrependUOffsetTRelative(fbs_udid)
        fbs_udids = builder.EndVector(len(fbs_udids))

        # pack car_ids
        fbs_car_ids = [
            builder.CreateString(udid) for udid in frozen_drivers['car_ids']
        ]
        FrozenDrivers.FrozenDriversStartCarIdsVector(builder, len(fbs_car_ids))
        for fbs_car_id in fbs_car_ids:
            builder.PrependUOffsetTRelative(fbs_car_id)
        fbs_car_ids = builder.EndVector(len(fbs_car_ids))

        FrozenDrivers.FrozenDriversStart(builder)
        FrozenDrivers.FrozenDriversAddUniqueDriverIds(builder, fbs_udids)
        FrozenDrivers.FrozenDriversAddCarIds(builder, fbs_car_ids)
        FrozenDrivers.FrozenDriversAddTimestamp(
            builder, frozen_drivers['timestamp'],
        )
        fbs_frozen_drivers = FrozenDrivers.FrozenDriversEnd(builder)

        builder.Finish(fbs_frozen_drivers)
        fbs_buffer = builder.Output()

        return gzip.compress(fbs_buffer)

    def add_calls(self, handler, calls=1):
        self.calls[handler] = self.calls.get(handler, 0) + calls

    def count_calls(self, handler=None):
        if handler is None:
            return sum(self.calls.values())
        return self.calls.get(handler, 0)

    def has_calls(self, handler=None):
        times_called = self.count_calls(handler)
        return bool(times_called)


@pytest.fixture(name='frozen_drivers_mocks')
def _frozen_drivers_mocks(mockserver):
    frozen_drivers_context = FrozenDriversContext()

    @mockserver.handler(_SERVICE + _FROZEN_URL)
    def _mock_frozen(request):
        frozen_drivers_context.add_calls(_FROZEN_URL)
        error = frozen_drivers_context.errors.get(_FROZEN_URL)
        if error is not None:
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )
        response_fbs = frozen_drivers_context.response_fbs
        if response_fbs is None:
            response_fbs = frozen_drivers_context.build_frozen_drivers(
                {'unique_driver_ids': [], 'car_ids': [], 'timestamp': 0},
            )
        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    return frozen_drivers_context


@pytest.fixture(name='frozen_drivers_fixture', autouse=True)
def _frozen_drivers_fixture(frozen_drivers_mocks, request):
    frozen_drivers_mocks.reset()

    marker = request.node.get_closest_marker(_FROZEN_MARKER)
    if marker:
        frozen_drivers_mocks.set_frozen_drivers(**marker.kwargs)

    yield frozen_drivers_mocks

    frozen_drivers_mocks.reset()
