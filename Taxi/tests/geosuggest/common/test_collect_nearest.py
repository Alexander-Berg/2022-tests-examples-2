from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.geosuggest.common import nile_blocks


def test_collect_nearest():
    request_input = [Record(lon=37.6427, lat=55.7340)]
    candidates_input = [
        Record(lon=37.6421, lat=55.7351, id=0),
        Record(lon=37.6417, lat=55.7361, id=1),
    ]
    expected_output = [
        Record(lon=37.6427, lat=55.7340, nearest_candidates=[0]),
    ]
    output = []

    job = clusters.MockCluster().job()

    nile_blocks.collect_nearest(
        requests=job.table('').label('request'),
        candidates=job.table('').label('candidates'),
        radius=200,
        geohash_precision=6,
        candidate_extractor='id',
    ).put('').label('output')

    job.local_run(
        sources={
            'request': StreamSource(request_input),
            'candidates': StreamSource(candidates_input),
        },
        sinks={'output': ListSink(output)},
    )

    assert output == expected_output
