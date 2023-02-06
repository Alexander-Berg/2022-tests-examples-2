import collections

from dateutil import parser
import pytest


Record = collections.namedtuple(
    'Record',
    [
        'legacy_depot_id',
        'timestamp',
        'pipeline',
        'load_level',
        'delivery_types',
    ],
)


@pytest.fixture(name='grocery_surge', autouse=True)
def mock_grocery_surge(mockserver):
    records = []

    @mockserver.json_handler('/grocery-surge/internal/v1/surge/update')
    def _mock_get_surge_update(request):
        time_from = request.json.get('time_from', None)
        if time_from is not None:
            time_from = parser.parse(time_from)
        cursor = int(request.json.get('cursor', '0'))
        limit = request.json.get('limit', 1000)
        active_only = request.json.get('active_only', True)

        data = []
        while cursor < len(records) and len(data) < limit:
            record = records[cursor]
            if (time_from is None or time_from <= record.timestamp) and (
                    not active_only or record.delivery_types
            ):
                data.append(
                    {
                        'depot_id': record.legacy_depot_id,
                        'surge_info': {'load_level': record.load_level},
                        'pipeline': record.pipeline,
                        'delivery_types': list(record.delivery_types),
                        'timestamp': record.timestamp.isoformat(),
                    },
                )
            cursor += 1
        return {'cursor': str(cursor), 'data': data}

    class Context:
        def add_record(
                self,
                *,
                legacy_depot_id,
                timestamp,
                pipeline,
                load_level,
                delivery_types=('pedestrian',),
        ):
            records.append(
                Record(
                    legacy_depot_id=legacy_depot_id,
                    timestamp=parser.parse(timestamp),
                    pipeline=pipeline,
                    load_level=load_level,
                    delivery_types=delivery_types,
                ),
            )

            return self

    context = Context()
    return context
