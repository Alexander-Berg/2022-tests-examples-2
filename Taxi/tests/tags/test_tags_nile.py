# coding: utf-8


import pytest
from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.tags import nile_blocks


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_timestamp_snapshot():
    job = clusters.MockCluster().job()
    snapshot_1 = nile_blocks.create_tags_snapshot(
        job.table('').label('input_1'),
    )
    snapshot_2 = nile_blocks.create_tags_snapshot(
        job.table('').label('input_2'),
    )

    nile_blocks.restore_tags_table(snapshot_1, 11).label('output_1').put('')
    nile_blocks.restore_tags_table(snapshot_1, 12).label('output_2').put('')
    nile_blocks.restore_tags_table(snapshot_1, 15).label('output_3').put('')

    nile_blocks.restore_tags_table(
        job.concat(snapshot_1, snapshot_2), 19,
    ).label('output_4').put('')

    output_1, output_2, output_3, output_4 = [], [], [], []
    job.local_run(
        sources={
            'input_1': StreamSource(
                [
                    Record(key=1, timestamp=8, tags=['a']),
                    Record(key=1, timestamp=9, tags=['a', 'b']),
                    Record(key=1, timestamp=10, tags=['a', 'b', 'c']),
                    Record(key=1, timestamp=11, tags=['b', 'c', 'd']),
                    Record(key=1, timestamp=12, tags=['b']),
                    Record(key=1, timestamp=14, tags=['a', 'e']),
                    Record(key=2, timestamp=9, tags=['2', '3']),
                    Record(key=3, timestamp=12, tags=['3', '4']),
                    Record(key=4, timestamp=19, tags=['4', '5']),
                    Record(key=5, timestamp=12, tags=['q']),
                    Record(key=5, timestamp=13, tags=None),
                    Record(key=6, timestamp=1, tags=['e']),
                    Record(key=6, timestamp=2, tags=None),
                    Record(key=6, timestamp=12, tags=['w']),
                ],
            ),
            'input_2': StreamSource(
                [
                    Record(key=1, timestamp=15, tags=['x', 'y']),
                    Record(key=1, timestamp=20, tags=['x', 'y', 'z']),
                ],
            ),
        },
        sinks={
            'output_1': ListSink(output_1),
            'output_2': ListSink(output_2),
            'output_3': ListSink(output_3),
            'output_4': ListSink(output_4),
        },
    )
    assert len(output_1) == 2
    assert len(output_2) == 5
    assert len(output_3) == 4
    assert len(output_4) == 5

    assert set(output_1[0].tags) == {'b', 'c', 'd'}
    assert set(output_1[1].tags) == {'2', '3'}

    assert set(output_2[0].tags) == {'b'}
    assert set(output_2[1].tags) == {'2', '3'}
    assert set(output_2[2].tags) == {'3', '4'}
    assert set(output_2[3].tags) == {'q'}
    assert set(output_2[4].tags) == {'w'}

    assert set(output_3[0].tags) == {'a', 'e'}
    assert set(output_3[1].tags) == {'2', '3'}
    assert set(output_3[2].tags) == {'3', '4'}
    assert set(output_3[3].tags) == {'w'}

    assert set(output_4[0].tags) == {'x', 'y'}
    assert set(output_4[1].tags) == {'2', '3'}
    assert set(output_4[2].tags) == {'3', '4'}
    assert set(output_4[3].tags) == {'4', '5'}
    assert set(output_4[4].tags) == {'w'}


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_timepoints_snapshot():
    job = clusters.MockCluster().job()
    snapshot_1 = nile_blocks.create_tags_snapshot(
        job.table('').label('input_1'),
    )
    snapshot_2 = nile_blocks.create_tags_snapshot(
        job.table('').label('input_2'),
    )
    timepoints = job.table('').label('input_3')

    nile_blocks.restore_tags_table(
        job.concat(snapshot_1, snapshot_2), timepoints,
    ).label('output').put('')

    output = []
    job.local_run(
        sources={
            'input_1': StreamSource(
                [
                    Record(key=1, timestamp=8, tags=['a']),
                    Record(key=1, timestamp=9, tags=['a', 'b']),
                    Record(key=1, timestamp=10, tags=['a', 'b', 'c']),
                    Record(key=1, timestamp=11, tags=['b', 'c', 'd']),
                    Record(key=1, timestamp=12, tags=['b']),
                    Record(key=1, timestamp=14, tags=['a', 'e']),
                    Record(key=2, timestamp=9, tags=['2', '3']),
                    Record(key=3, timestamp=12, tags=['3', '4']),
                    Record(key=4, timestamp=19, tags=['4', '5']),
                    Record(key=5, timestamp=12, tags=['q']),
                    Record(key=5, timestamp=13, tags=None),
                    Record(key=6, timestamp=1, tags=['e']),
                    Record(key=6, timestamp=2, tags=None),
                    Record(key=6, timestamp=12, tags=['w']),
                ],
            ),
            'input_2': StreamSource(
                [
                    Record(key=1, timestamp=15, tags=['x', 'y']),
                    Record(key=1, timestamp=20, tags=['x', 'y', 'z']),
                ],
            ),
            'input_3': StreamSource(
                [
                    Record(key=1, timestamp=8),
                    Record(key=1, timestamp=9),
                    Record(key=1, timestamp=10),
                    Record(key=1, timestamp=11),
                    Record(key=1, timestamp=12),
                    Record(key=1, timestamp=14),
                    Record(key=2, timestamp=9),
                    Record(key=3, timestamp=12),
                    Record(key=4, timestamp=19),
                    Record(key=1, timestamp=15),
                    Record(key=1, timestamp=20),
                    Record(key=5, timestamp=1),
                    Record(key=5, timestamp=12),
                    Record(key=5, timestamp=13),
                    Record(key=6, timestamp=1),
                    Record(key=6, timestamp=2),
                    Record(key=6, timestamp=12),
                    Record(key=6, timestamp=13),
                ],
            ),
        },
        sinks={'output': ListSink(output)},
    )
    assert len(output) == 18

    assert set(output[0].tags) == {'a'}
    assert set(output[1].tags) == {'a', 'b'}
    assert set(output[2].tags) == {'a', 'b', 'c'}
    assert set(output[3].tags) == {'b', 'c', 'd'}
    assert set(output[4].tags) == {'b'}
    assert set(output[5].tags) == {'a', 'e'}
    assert set(output[6].tags) == {'x', 'y'}
    assert set(output[7].tags) == {'x', 'y', 'z'}
    assert set(output[8].tags) == {'2', '3'}
    assert set(output[9].tags) == {'3', '4'}
    assert set(output[10].tags) == {'4', '5'}
    assert output[11].tags is None
    assert set(output[12].tags) == {'q'}
    assert output[13].tags is None
    assert set(output[14].tags) == {'e'}
    assert output[15].tags is None
    assert set(output[16].tags) == {'w'}
    assert set(output[17].tags) == {'w'}
