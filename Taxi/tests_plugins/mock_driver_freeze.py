import gzip
import io
import json
import time

import flatbuffers
import pytest

import fbs.models.detail.FrozenDrivers as FbsFrozenDrivers


class DriverFreezeContext:
    def __init__(self):
        self.unique_driver_ids = set()
        self.car_ids = set()

    def freeze(self, unique_driver_id, car_id):
        if unique_driver_id in self.unique_driver_ids:
            return False
        if car_id in self.car_ids:
            return False
        self.unique_driver_ids.add(unique_driver_id)
        self.car_ids.add(car_id)
        return True


@pytest.fixture(autouse=True)
def driver_freeze(mockserver):
    context = DriverFreezeContext()

    def _create_string_vector(builder, ids):
        id_count = len(ids)
        id_offsets = [builder.CreateString(id) for id in ids]

        builder.StartVector(4, id_count, 4)
        for pos in id_offsets:
            builder.PrependUOffsetTRelative(pos)
        return builder.EndVector(id_count)

    def _gzip_builder(builder):
        object_bytes = bytes(builder.Output())

        data = io.BytesIO()
        with gzip.GzipFile(mode='wb', fileobj=data) as zfle:
            zfle.write(object_bytes)
        return data.getvalue()

    @mockserver.json_handler('/driver-freeze/frozen')
    def _mock_frozen(request):
        builder = flatbuffers.Builder(0)

        unique_driver_ids = _create_string_vector(
            builder, context.unique_driver_ids,
        )
        car_ids = _create_string_vector(builder, context.car_ids)
        timestamp = int(time.time())

        FbsFrozenDrivers.FrozenDriversStart(builder)
        FbsFrozenDrivers.FrozenDriversAddUniqueDriverIds(
            builder, unique_driver_ids,
        )
        FbsFrozenDrivers.FrozenDriversAddCarIds(builder, car_ids)
        FbsFrozenDrivers.FrozenDriversAddTimestamp(builder, timestamp)
        obj = FbsFrozenDrivers.FrozenDriversEnd(builder)

        builder.Finish(obj)
        data = _gzip_builder(builder)

        unique_driver_ids = context.unique_driver_ids
        car_ids = context.car_ids

        return mockserver.make_response(
            response=data,
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler('/driver-freeze/freeze')
    def _mock_freeze(request):
        data = json.loads(request.get_data())
        unique_driver_id = data['unique_driver_id']
        car_id = data['car_id']
        return {'freezed': context.freeze(unique_driver_id, car_id)}

    @mockserver.json_handler('/driver-freeze/freeze-bulk')
    def _mock_freeze_bulk(request):
        data = json.loads(request.get_data())
        drivers = data['drivers']

        freezed = []
        for driver in drivers:
            unique_driver_id = driver['unique_driver_id']
            car_id = driver['car_id']
            freezed.append(
                {
                    'unique_driver_id': unique_driver_id,
                    'freezed': context.freeze(unique_driver_id, car_id),
                },
            )

        return {'drivers': freezed}

    return context
