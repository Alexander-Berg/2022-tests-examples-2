from typing import NamedTuple, AnyStr

import json
from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.geosuggest.common import nile_blocks


class Object(NamedTuple):
    lon: float
    lat: float

    def to_json(self) -> str:
        return json.dumps(self._asdict())

    @staticmethod
    def from_json(doc: AnyStr):
        return Object(**json.loads(doc))


class Similarity:
    def __call__(self, obj1, obj2):
        return abs(obj1.lat - obj2.lat) < 0.001


def test_sparsify():
    objects_input = [
        Record(
            object=Object(lon=37.6427, lat=55.7339).to_json(),
            lon=37.6427,
            lat=55.7339,
        ),
        Record(
            object=Object(lon=37.6421, lat=55.7361).to_json(),
            lon=37.6421,
            lat=55.7361,
        ),
        Record(
            object=Object(lon=37.6417, lat=55.7351).to_json(),
            lon=37.6417,
            lat=55.7351,
        ),
    ]
    expected_output = [
        Record(
            object=Object(lon=37.6427, lat=55.7339).to_json(),
            lon=37.6427,
            lat=55.7339,
        ),
        Record(
            object=Object(lon=37.6421, lat=55.7361).to_json(),
            lon=37.6421,
            lat=55.7361,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()
    objects = job.table('').label('objects')
    nile_blocks.sparsify(
        objects=objects,
        create_similarity_extractor=lambda: Similarity(),
        create_object_parser=lambda: Object.from_json,
        priority_extractor='lon',
        object_extractor='object',
        geohash_precision=6,
    ).put('').label('output')

    job.local_run(
        sources={'objects': StreamSource(objects_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output
