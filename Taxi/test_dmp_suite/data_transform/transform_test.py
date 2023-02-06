from copy import copy

import pytest

from dmp_suite import data_transform as dt
from dmp_suite.table import Table, Field


def test_map():
    def m(doc):
        result = copy(doc)
        result['a'] = doc['a'] + 1
        return result

    mapper = dt.Map(m)

    source = dict(a=1, b=3)
    expected = dict(a=2, b=3)
    assert mapper.apply(source) == expected
    assert list(mapper([source])) == [expected]


def test_map_on_empty_data():
    assert list(dt.Map(lambda d: d)([])) == []


def test_filter():
    f = dt.Filter(lambda d: d['a'] == 1)
    source = [dict(a=1, b=1), dict(a=2, b=1)]
    expected = [dict(a=1, b=1)]
    assert list(f(source)) == expected
    assert f.check(source[0])
    assert not f.check(source[1])


def test_project():
    project = dt.Project(
        'a',
        b='bb',
        c='c.c',
        d=lambda d: d['d'] + 10,
    )
    source = dict(
        a=1,
        bb=2,
        c=dict(c=3),
        d=4,
    )
    expected = dict(
        a=1,
        b=2,
        c=3,
        d=14,
    )
    assert project.apply(source) == expected
    assert list(project([source])) == [expected]


def test_project_as_nile_project_test():
    project = dt.Project(
        a='b',
        b='c',
        c='a',
    )
    assert project.apply(dict(a=1, b=2, c=3)) == dict(a=2, b=3, c=1)


def test_project_extractors_as_dict():
    extractors = dict(
        b='bb',
        c='c.c',
        d=lambda d: d['d'] + 10,
    )
    project = dt.Project(
        'a',
        'd',
        extractors=extractors,
        d=lambda d: d['d'] + 20,
    )
    source = dict(
        a=1,
        bb=2,
        c=dict(c=3),
        d=4,
    )
    expected = dict(
        a=1,
        b=2,
        c=3,
        d=24,
    )
    assert project.apply(source) == expected
    assert list(project([source])) == [expected]


def test_project_wrong_extractor_func():
    with pytest.raises(ValueError):
        dt.Project(a=lambda a, b, c: a + b + c)


def test_project_from_table():
    class T(Table):
        a = Field()
        b = Field()

    project = dt.Project.from_table(T, b='c')
    assert project.apply(dict(a=1, b=2, c=3)) == dict(a=1, b=3)


def test_project_from_table_wrong_extractor():
    class T(Table):
        a = Field()
        b = Field()

    with pytest.raises(ValueError):
        dt.Project.from_table(T, c='c')


def test_serialize():
    fields = [
        Field(name='a', serializer=int),
        Field(name='b', serializer=str),
        Field(name='c'),
        Field(name='d', default_value='e'),
    ]

    serialize = dt.Serialize(fields)
    source = dict(a='111', b=23.2, c=1, e=10)
    assert serialize.apply(source) == dict(a=111, b='23.2', c=1, d='e')


def test_serialize_from_table():
    class T(Table):
        a = Field()
        b = Field()

    serialize = dt.Serialize.from_table(T)
    source = dict(a='111', b=23.2, c=1, e=10)
    assert serialize.apply(source) == dict(a='111', b=23.2)


def test_extend():
    extend = dt.Extend(a=lambda d: 10, b='c')
    assert extend.apply(dict(e=1, c=5)) == dict(a=10, b=5, c=5, e=1)


def test_flat_map():
    def fm(doc):
        yield doc
        yield doc

    flat_map = dt.FlatMap(fm)
    source = [dict(a=1)]
    assert list(flat_map(source)) == [dict(a=1), dict(a=1)]


def test_flat_map_empty_source():
    def fm(doc):
        yield doc
        yield doc

    flat_map = dt.FlatMap(fm)
    assert list(flat_map([])) == []


def test_unfold_dict_list():
    unfold = dt.UnfoldDictList(path='a', b='c')
    source = [dict(a=[dict(d=1), dict(d=2)], c=5)]
    assert list(unfold(source)) == [dict(b=5, d=1), dict(b=5, d=2)]


def test_unfold_dict_list_empty_source():
    unfold = dt.UnfoldDictList(path='a', b='c')
    assert list(unfold([dict(b=10)])) == []
    assert list(unfold([dict(b=10, a=None)])) == []
    assert list(unfold([])) == []


def test_unfold():
    unfold = dt.Unfold(path='a', unfold_to='a', b='c')
    source = [dict(a=[dict(d=1), dict(d=2)], c=5)]
    expected = [dict(a=dict(d=1), b=5), dict(a=dict(d=2), b=5)]
    assert list(unfold(source)) == expected

    unfold = dt.Unfold(path='a', unfold_to='b', c='c')
    source = [dict(a=[1, 2, 3], c=5)]
    expected = [dict(b=1, c=5), dict(b=2, c=5), dict(b=3, c=5)]
    assert list(unfold(source)) == expected


def test_unfold_empty_source():
    unfold = dt.Unfold(path='a', unfold_to='a')
    assert list(unfold([dict(b=10)])) == []
    assert list(unfold([dict(b=10, a=None)])) == []
    assert list(unfold([])) == []


def test_qb2_transform():
    from qb2.api.v1 import extractors as qe
    from qb2.api.v1 import filters as qf

    qb2 = dt.QB2Transform(
        fields=[
            qe.log_field('a'),
            qe.log_field('b').rename('c'),
        ],
        filters=[
            qf.equals('a', 1)
        ]
    )

    source = [dict(a=1, b=2, c=3), dict(a=2, b=3, c=4)]
    assert list(qb2(source)) == [dict(a=1, c=2)]


def test_chunked():
    class TestTransform(dt.ChunkedTransform):
        chunk_num = 0
        def transform_chunk(self, chunk):
            self.chunk_num += 1
            return [
                f'{item} processed in chunk {self.chunk_num}'
                for item in chunk
            ]

    items = range(7)
    transformation = TestTransform(chunk_size=3)
    results = list(transformation.transform(items))

    assert len(results) == 7

    expected = [
        '0 processed in chunk 1',
        '1 processed in chunk 1',
        '2 processed in chunk 1',
        '3 processed in chunk 2',
        '4 processed in chunk 2',
        '5 processed in chunk 2',
        '6 processed in chunk 3',
    ]
    assert results == expected


def test_custom_error_on_extractor_exc():
    project = dt.Project(
        a=lambda doc: doc['b'],
    )

    assert project.apply({'b': 1}) == {'a': 1}

    invalid_doc = {'c': 1}
    with pytest.raises(dt.TransformError, match=str(invalid_doc)):
        assert project.apply(invalid_doc) == {'a': 1}
