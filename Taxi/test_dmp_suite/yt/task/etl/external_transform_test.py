import pytest
import pandas

from dmp_suite.data_transform import Map
from dmp_suite.yt import etl
from dmp_suite.yt import operation as yt
from dmp_suite.yt.task.etl import transform
from dmp_suite.yt.task.etl.external_transform import (
    external_source,
)
from dmp_suite.task.external_source import ExternalSourceError
from test_dmp_suite.yt import utils
from test_dmp_suite.yt.task.etl.utils import MockTask, Table

table = utils.fixture_random_yt_table(Table)

DATA = [dict(a=1), dict(b=2)]


def foo():
    yield from DATA


def foo_as_dataframe():
    # Исходные данные содержат словари с разными полями.
    # Если в записи нет какого-то поля, то Pandas
    # вставит в запись NaN.
    # Нам важно, чтобы ExternalSource не возвращал такие поля,
    # потому что мы не сможем записать numpy.sNaN в YT или GP.
    return pandas.DataFrame(foo())


def foo_to_much_args(a, b, c):
    yield dict()


@pytest.mark.parametrize('data', [foo(), foo_to_much_args])
def test_external_source_wrong_data_types(data):
    with pytest.raises(ExternalSourceError):
        list(external_source(data).get_value(None, None).get_data())


@pytest.mark.parametrize('data', [
    foo,
    # Если функция возвращает дата-фреймы, то результат извлечения данных
    # из source должен содержать только те колонки, которые не NaN.
    foo_as_dataframe,
    DATA
])
def test_external_source_get_data(data):
    assert list(external_source(data).get_value(None, None).get_data()) == DATA


def test_external_source_with_dataframe():
    items = [
        {'name': 'Vasily'},
        {'name': 'Olga'},
    ]
    def get_dataframe():
        return pandas.DataFrame(items)

    assert list(external_source(get_dataframe).get_value(None, None).get_data()) == items


def test_external_source_pass_args():
    def foo_with_args(args):
        yield dict(a=args['a'])

    source = external_source(foo_with_args).get_value(dict(a=1), None)
    assert list(source.get_data()) == [dict(a=1)]


def test_external_source_pass_args_and_env():
    def foo_with_args(args, env):
        yield dict(a=args['a'], b=env['b'])

    source = external_source(foo_with_args).get_value(dict(a=1), dict(b=2))
    assert list(source.get_data()) == [dict(a=1, b=2)]


@pytest.mark.slow
def test_external_source_writes(table):
    data = [
        dict(a=1, b=1),
        dict(a=2, b=2),
    ]
    env = transform.TransformationEnvironment(task=MockTask())
    path_factory = etl.temporary_buffer_table(table)

    source = external_source(data).get_value(None, env)
    with source.source_table(path_factory) as src:
        assert data == list(yt.read_yt_table(src))

    data_for_extractors = [
        dict(a=1, c=1),
        dict(a=2, c=2),
    ]
    accessor = external_source(data_for_extractors, dict(b=lambda d: d['c']))
    source = accessor.get_value(None, env)
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as src:
        assert data == list(yt.read_yt_table(src))


@pytest.mark.slow
def test_external_source_with_transform(table):
    data = [dict(a=1), dict(b=2)]
    env = transform.TransformationEnvironment(task=MockTask())
    path_factory = etl.temporary_buffer_table(table)

    def trns(doc):
        return dict(a=doc.get('a') or doc.get('b'))

    accessor = external_source(data=data, transform=Map(trns))
    source = accessor.get_value(None, env)
    with source.source_table(path_factory) as src:
        expected = [dict(a=1, b=None), dict(a=2, b=None)]
        assert list(yt.read_yt_table(src)) == expected

    accessor = external_source(
        data=data,
        transform=Map(trns),
        extractors=dict(b=lambda d: d['a'])
    )
    source = accessor.get_value(None, env)
    path_factory = etl.temporary_buffer_table(table)
    with source.source_table(path_factory) as src:
        expected = [dict(a=1, b=1), dict(a=2, b=2)]
        assert list(yt.read_yt_table(src)) == expected
