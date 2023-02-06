from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.geosuggest.common import geohash


def test_get_geohash():
    assert geohash.get_geohash(lon=37.6421, lat=55.7351) == 'ucfv0d60kx8j'
    assert geohash.get_geohash(lon=1000, lat=-1000) is None


def test_add_geohash():
    lon, lat = 37.6421, 55.7351

    job = clusters.MockCluster().job()
    geohash.add_geohash(job.table('').label('input'), precision=12).label(
        'output',
    ).put('')

    input = [Record(lon=lon, lat=lat)]
    output = []
    job.local_run(
        sources={'input': StreamSource(input)},
        sinks={'output': ListSink(output)},
    )

    assert output == [Record(lon=lon, lat=lat, geohash='ucfv0d60kx8j')]


def test_expand_geohash():
    lon, lat = 37.6421, 55.7351

    job = clusters.MockCluster().job()
    geohash.add_expanded_geohash(
        job.table('').label('input'), precision=4, unfold=True,
    ).label('output').put('')

    input = [Record(lon=lon, lat=lat)]
    output = []
    job.local_run(
        sources={'input': StreamSource(input)},
        sinks={'output': ListSink(output)},
    )

    geohashes = [
        'ucft',
        'ucgj',
        'ucfu',
        'ucfs',
        'ucgh',
        'ucfy',
        'ucfw',
        'ucgn',
        'ucfv',
    ]
    assert output == [Record(lon=lon, lat=lat, geohash=g) for g in geohashes]
