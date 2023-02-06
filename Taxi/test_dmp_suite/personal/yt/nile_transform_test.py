import operator
import pytest
import typing as tp

from nile.api.v1 import MockCluster, Record, Job
from nile.local.source import StreamSource
from nile.local.sink import ListSink

from dmp_suite.personal.yt import (
    nile_transform,
    pd_types,
    tables as pd_tables,
    task as personal_task,
)
from dmp_suite.yt.task.etl.transform import date_range, target
from .tables import (
    NoDocFieldTable,
    PartitionedRawTable,
    RawTable,
    WrongTyprDocFieldTable,
)


def run_job(
        job: Job,
        sources: tp.Dict[str, tp.List[tp.Dict]],
        sinks: tp.Dict[str, tp.List],
):
    sources = {
        name: StreamSource([Record.from_dict(r) for r in data])
        for name, data in sources.items()
    }
    sinks = {
        name: ListSink(sink)
        for name, sink in sinks.items()
    }
    job.local_run(sources=sources, sinks=sinks)


def apply_replace_natural_value_in_raw(
        raw_data: tp.List[tp.Dict],
        mapping_data: tp.List[tp.Dict],
        natural_value_path: str,
        mapping_pd_id_field: str,
        mapping_natural_value_field: str,
        pd_id_path: tp.Optional[str] = None,
        natural_value_transform: tp.Optional[tp.Callable[[str], str]] = None,
        raise_on_not_found_pd_id: bool = True,
):
    job = MockCluster().job()
    raw = job.table('raw').label('raw')
    mapping = job.table('mapping').label('mapping')

    nile_transform.replace_natural_value_in_raw_with_mapping(
        stream=raw,
        mapping_stream=mapping,
        natural_value_path=natural_value_path,
        mapping_pd_id_field=mapping_pd_id_field,
        mapping_natural_value_field=mapping_natural_value_field,
        pd_id_path=pd_id_path,
        natural_value_transform=natural_value_transform,
        raise_on_not_found_pd_id=raise_on_not_found_pd_id,
    ).label('result').put('result')

    result = []
    run_job(
        job,
        sources=dict(raw=raw_data, mapping=mapping_data),
        sinks=dict(result=result),
    )
    return [r.to_dict() for r in result]


@pytest.mark.parametrize('path, raw_data, expected', [
    (
        'pd',
        [
            dict(id='a', doc=dict(pd=10)),
            dict(id='b', doc=dict(c=1)),
        ],
        [
            dict(id='a', doc=dict(pd='1')),
            dict(id='b', doc=dict(c=1)),
        ],
    ),
    (
        'a.pd',
        [
            dict(id='a', doc=dict(a=dict(pd=10))),
            dict(id='b', doc=dict(a=dict(c=1))),
        ],
        [
            dict(id='a', doc=dict(a=dict(pd='1'))),
            dict(id='b', doc=dict(a=dict(c=1))),
        ],
    ),
])
def test_replace_natural_value_in_raw_in_place(path, raw_data, expected):
    result = apply_replace_natural_value_in_raw(
        raw_data=raw_data,
        mapping_data=[dict(id='1', val=10)],
        natural_value_path=path,
        mapping_pd_id_field='id',
        mapping_natural_value_field='val',
    )
    assert sorted(result, key=operator.itemgetter('id')) == expected


@pytest.mark.parametrize('path, raw_data, expected', [
    (
        'pd',
        [
            dict(id='a', doc=dict(pd=10)),
            dict(id='b', doc=dict(c=10)),
        ],
        [
            dict(id='a', doc=dict(pd=10, pd_id='1')),
            dict(id='b', doc=dict(c=10)),
        ],
    ),
    (
        'a.pd',
        [
            dict(id='a', doc=dict(a=dict(pd=10))),
            dict(id='b', doc=dict(a=dict(c=10))),
        ],
        [
            dict(id='a', doc=dict(a=dict(pd=10), pd_id='1')),
            dict(id='b', doc=dict(a=dict(c=10))),
        ],
    ),
])
def test_replace_natural_value_in_raw_add_new_field(path, raw_data, expected):
    result = apply_replace_natural_value_in_raw(
        raw_data=raw_data,
        mapping_data=[dict(id='1', val=10)],
        natural_value_path=path,
        pd_id_path='pd_id',
        mapping_pd_id_field='id',
        mapping_natural_value_field='val',
    )
    assert sorted(result, key=operator.itemgetter('id')) == expected


def test_replace_natural_value_in_raw_raise_on_not_found_pd_id():
    with pytest.raises(Exception, match='ReplaceNaturalValueError'):
        apply_replace_natural_value_in_raw(
            raw_data=[dict(id='a', doc=dict(pd=10))],
            mapping_data=[dict(id='1', val=20)],
            natural_value_path='pd',
            mapping_pd_id_field='id',
            mapping_natural_value_field='val',
            raise_on_not_found_pd_id=True,
        )


def test_replace_natural_value_in_raw_only_string_in_path():
    with pytest.raises(Exception, match='Only strings supported in pd_id_path'):
        apply_replace_natural_value_in_raw(
            raw_data=[dict(id='a', doc=dict(pd=10))],
            mapping_data=[dict(id='1', val=20)],
            natural_value_path='pd.1',
            mapping_pd_id_field='id',
            mapping_natural_value_field='val',
            raise_on_not_found_pd_id=True,
        )


def test_replace_natural_value_in_raw_natural_value_transform():
    result = apply_replace_natural_value_in_raw(
        raw_data=[dict(id='a', doc=dict(a=1))],
        mapping_data=[dict(id='2', val=2)],
        natural_value_path='a',
        natural_value_transform=lambda v: v + 1,
        mapping_pd_id_field='id',
        mapping_natural_value_field='val',
        raise_on_not_found_pd_id=True,
    )
    assert result == [dict(id='a', doc=dict(a='2'))]


@pytest.mark.parametrize('path, raw_data, natural_value_transform, additional_fields, with_unique_flg, expected', [
    (
        'pd',
        [dict(id='a', doc=dict(pd=1)), dict(id='b', doc=dict(pd=2))],
        None,
        None,
        True,
        [dict(natural_value=1)],
    ),
    (
        'a.pd',
        [
            dict(id='a', doc=dict(a=dict(pd=1))),
            dict(id='b', doc=dict(a=dict(pd=2))),
        ],
        None,
        None,
        True,
        [dict(natural_value=1)],
    ),
    (
        'pd',
        [dict(id='a', doc=dict(pd=0)), dict(id='b', doc=dict(pd=1))],
        lambda v: v + 1,
        None,
        True,
        [dict(natural_value=1)],
    ),
    (
        'a.pd',
        [
            dict(id='a', doc=dict(a=dict(pd=0))),
            dict(id='b', doc=dict(a=dict(pd=1))),
        ],
        lambda v: v + 1,
        None,
        True,
        [dict(natural_value=1)],
    ),
    (
        'phone',
        [dict(id='a', doc=dict(phone='1234567890')), ],
        lambda phone: f'+{phone}',
        None,
        True,
        [dict(natural_value='+1234567890')],
    ),
    (
        'phone',
        [dict(id='a', doc=dict(id='b', phone='1234567890')), ],
        lambda phone: f'+{phone}',
        ['id'],
        True,
        [dict(id='a', natural_value='+1234567890')],
    ),
    (
        'phone',
        [
            dict(id='A', doc=dict(id='a', phone='1234567890')),
            dict(id='B', doc=dict(id='b', phone='1234567890')),
        ],
        lambda phone: f'+{phone}',
        ['id'],
        False,
        [
            dict(id='A', natural_value='+1234567890'),
            dict(id='B', natural_value='+1234567890')
        ],
    ),
    (
        'phone',
        [
            dict(id='A', doc=dict(id='a', phone='1234567890')),
            dict(id='B', doc=dict(id='b', phone='1234567890')),
        ],
        None,
        ['id', 'doc'],
        False,
        [
            dict(id='A', natural_value='1234567890', doc=dict(id='a', phone='1234567890')),
            dict(id='B', natural_value='1234567890', doc=dict(id='b', phone='1234567890')),
        ],
    ),
])
def test_find_natural_values_without_pd_id_mapping_in_raw(
        path, raw_data, natural_value_transform, additional_fields, with_unique_flg, expected,
):
    job = MockCluster().job()
    raw = job.table('raw').label('raw')
    mapping = job.table('mapping').label('mapping')
    nile_transform.find_without_mapping_in_raw(
        stream=raw,
        mapping_stream=mapping,
        natural_value_path=path,
        mapping_natural_value_field='val',
        natural_value_transform=natural_value_transform,
        additional_fields=additional_fields,
        with_unique_flg=with_unique_flg
    ).label('result').put('result')
    result = []
    run_job(
        job,
        sources=dict(
            raw=raw_data,
            mapping=[dict(id='2', val=2)],
        ),
        sinks=dict(result=result),
    )
    result = [r.to_dict() for r in result]
    assert result == expected


@pytest.mark.parametrize('path, raw_data, expected', [
    (
        'pd',
        [dict(id='a', doc=dict(pd=10))],
        [dict(id='a', doc=dict())],
    ),
    (
        'pd',
        [dict(id='a', doc=dict(a=1, pd=10))],
        [dict(id='a', doc=dict(a=1))],
    ),
    (
        'pd',
        [dict(id='a', doc=dict(a=1))],
        [dict(id='a', doc=dict(a=1))],
    ),
    (
        'a.pd',
        [dict(id='a', doc=dict(a=dict(pd=10)))],
        [dict(id='a', doc=dict(a=dict()))],
    ),
    (
        'a.pd',
        [dict(id='a', doc=dict(a=dict(pd=10, c=1), b=10))],
        [dict(id='a', doc=dict(a=dict(c=1), b=10))],
    ),
    (
        'a.pd',
        [dict(id='a', doc=dict(b=10))],
        [dict(id='a', doc=dict(b=10))],
    ),
])
def test_drop_natural_value(path, raw_data, expected):
    job = MockCluster().job()
    raw = job.table('raw').label('raw')
    nile_transform.drop_natural_value_in_raw(
        raw,
        natural_value_path=path,
    ).label('result').put('result')
    result = []
    run_job(
        job,
        sources=dict(raw=raw_data),
        sinks=dict(result=result),
    )
    result = [r.to_dict() for r in result]
    assert result == expected


@pytest.mark.parametrize('table', [
    NoDocFieldTable,
    WrongTyprDocFieldTable,
])
def test_raw_source_fails_on_bad_table(table):
    with pytest.raises(personal_task.PdMigrationTaskError):
        nile_transform.RawSource(table)


@pytest.mark.parametrize('table, path', [
    (RawTable, target),
    (PartitionedRawTable, date_range),
])
def test_source_path_configuration(table, path):
    source = nile_transform.RawSource(table)
    assert isinstance(source.get_source().stream_defs['raw'], path)


@pytest.mark.parametrize('paths', [
    ['a.b'],
    ['a.b', 'a.b.c'],
])
def test_source_replace_configuration(paths):
    source = nile_transform.RawSource(RawTable)
    pd_type = pd_types.PdType(value_field='val', table=pd_tables.PersonalTable)

    for path in paths:
        source = (
            source.replace_pd(natural_value_path=path, pd_type=pd_type)
            .drop_natural_value(natural_value_path=path)
        )

    commands = list(reversed(source._commands))
    for path in paths:
        cmd = commands.pop()
        assert cmd.func is nile_transform.replace_pd_value_in_raw
        assert cmd.params['natural_value_path'] == path
        cmd = commands.pop()
        assert cmd.func is nile_transform.drop_natural_value_in_raw
        assert cmd.params['natural_value_path'] == path

    assert not commands

    source = nile_transform.RawSource(RawTable)

    for path in paths:
        source = (
            source.add_pd_id(
                natural_value_path=path,
                pd_type=pd_type,
                pd_id_path=path + '_id',
            )
            .add_pd_id(natural_value_path=path, pd_type=pd_type)
            .drop_natural_value(natural_value_path=path)
        )

    commands = list(reversed(source._commands))
    for path in paths:
        cmd = commands.pop()
        assert cmd.func is nile_transform.replace_pd_value_in_raw
        assert cmd.params['natural_value_path'] == path
        assert cmd.params['pd_id_path'] == path + '_id'
        cmd = commands.pop()
        assert cmd.func is nile_transform.replace_pd_value_in_raw
        assert cmd.params['natural_value_path'] == path
        assert cmd.params['pd_id_path'] == path + '_pd_id'
        cmd = commands.pop()
        assert cmd.func is nile_transform.drop_natural_value_in_raw
        assert cmd.params['natural_value_path'] == path
