import json

import pytest
import yt.yson


@pytest.mark.parametrize('mode_of_get', ['by_index', 'by_name'])
@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_lookup_rows(taxi_userver_ytlib_sample, yt_apply, mode_of_get):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/foo',
            'ids': ['bar', 'foo'],
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'id': 'bar', 'value': 'def'},
            {'id': 'foo', 'value': 'abc'},
        ],
    }


@pytest.mark.parametrize('mode_of_get', ['by_index', 'by_name'])
@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_lookup_rows_force_yt(
        taxi_userver_ytlib_sample, yt_apply_force, mode_of_get,
):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/foo',
            'ids': ['bar', 'foo'],
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'id': 'bar', 'value': 'def'},
            {'id': 'foo', 'value': 'abc'},
        ],
    }


@pytest.mark.parametrize('mode_of_get', ['by_index', 'by_name'])
async def test_lookup_rows_service_schemas(
        taxi_userver_ytlib_sample, yt_apply, mode_of_get,
):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/bar',
            'ids': ['bar', 'foo'],
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.parametrize(
    'yt_table, mode_of_get',
    [
        ('//home/testsuite/foo', 'by_name'),
        ('//home/testsuite/any', 'parse_any'),
    ],
)
@pytest.mark.yt(
    schemas=['yt_foo_schema.yaml'],
    dyn_table_data=[
        {
            'path': '//home/testsuite/foo',
            'values': [{'id': 'foo', 'value': 'abc'}],
        },
        {
            'path': '//home/testsuite/foo',
            'values': [
                {'id': 'bytes', 'value': b'raw-bytes'},
                {'id': 'bytes_0', 'value': b'test\x00test'},
            ],
            'format': {'encoding': None},
        },
        {
            'path': '//home/testsuite/any',
            'values': [{'id': 'foo', 'value': 'abc'}],
        },
        {
            'path': '//home/testsuite/any',
            'values': [
                {'id': 'bytes', 'value': b'raw-bytes'},
                {'id': 'bytes_0', 'value': b'test\x00test'},
            ],
            'format': {'encoding': None},
        },
    ],
)
@pytest.mark.parametrize(
    'id_to_get,expected_value',
    [('foo', 'abc'), ('bytes', 'raw-bytes'), ('bytes_0', 'test\x00test')],
)
async def test_lookup_rows_parse_any(
        taxi_userver_ytlib_sample,
        yt_apply,
        yt_table,
        mode_of_get,
        id_to_get,
        expected_value,
        yt_client,
):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': yt_table,
            'ids': [id_to_get],
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [{'id': id_to_get, 'value': expected_value}],
    }


_YSON_VALUE = {
    'key': yt.yson.to_yson_type('subkey', attributes={'attr': 'attr_value'}),
    'key2': 'test_value',
    'created': yt.yson.to_yson_type(
        '2020-10-14T13:03:21.500124', attributes={'raw_type': 'datetime'},
    ),
}
_YSON_VALUE_LIST = {
    'key': yt.yson.to_yson_type(
        ['test'],
        attributes={
            'subkey_attr': 'subkey_extra_attr',
            'subkey_attr2': 'subkey_extra_attr2',
        },
    ),
}
_YSON_VALUE_COMPLICATED = {
    'key': yt.yson.to_yson_type(
        [
            yt.yson.to_yson_type(
                'subkey', attributes={'subkey_attr': 'subkey_extra_attr'},
            ),
            yt.yson.to_yson_type(
                {'map_key': 'map_value'},
                attributes={'map_attr': 'map_extra_attr'},
            ),
        ],
        attributes={'attr': 'attr_value'},
    ),
}

_YSON_VALUE_DEEP_ATTRS = {
    'key': yt.yson.to_yson_type(
        'value',
        attributes={
            'subkey_attr': yt.yson.to_yson_type(
                'subkey_extra_attr', attributes={'x': 'y'},
            ),
        },
    ),
}

_YSON_WITH_LIST = {
    'key': yt.yson.to_yson_type(
        [
            yt.yson.to_yson_type('string', attributes={'x': 'y'}),
            yt.yson.to_yson_type(
                {
                    'subkey': yt.yson.to_yson_type(
                        {'subkey2': 'subvalue'},
                        attributes={'subattr': 'subattrvalue'},
                    ),
                },
                attributes={'x': 'y'},
            ),
        ],
        attributes={'x': 'y'},
    ),
}


@pytest.mark.parametrize(
    'input_obj, mode_of_get, expected_json',
    [
        (
            _YSON_VALUE,
            'parse_attrs',
            {
                'key': {'$v': 'subkey', '$a': {'attr': 'attr_value'}},
                'key2': 'test_value',
                'created': {
                    '$v': '2020-10-14T13:03:21.500124',
                    '$a': {'raw_type': 'datetime'},
                },
            },
        ),
        (
            _YSON_VALUE,
            'parse_json',
            {
                'key': 'subkey',
                'key2': 'test_value',
                'created': '2020-10-14T13:03:21.500124',
            },
        ),
        (None, 'parse_optional_attrs', None),
        (_YSON_VALUE_LIST, 'parse_json', {'key': ['test']}),
        (
            _YSON_VALUE_LIST,
            'parse_attrs',
            {
                'key': {
                    '$a': {
                        'subkey_attr': 'subkey_extra_attr',
                        'subkey_attr2': 'subkey_extra_attr2',
                    },
                    '$v': ['test'],
                },
            },
        ),
        (
            _YSON_VALUE_COMPLICATED,
            'parse_json',
            {'key': ['subkey', {'map_key': 'map_value'}]},
        ),
        (
            _YSON_VALUE_COMPLICATED,
            'parse_attrs',
            {
                'key': {
                    '$a': {'attr': 'attr_value'},
                    '$v': [
                        {
                            '$a': {'subkey_attr': 'subkey_extra_attr'},
                            '$v': 'subkey',
                        },
                        {
                            '$a': {'map_attr': 'map_extra_attr'},
                            '$v': {'map_key': 'map_value'},
                        },
                    ],
                },
            },
        ),
        (_YSON_VALUE_DEEP_ATTRS, 'parse_json', {'key': 'value'}),
        (
            _YSON_VALUE_DEEP_ATTRS,
            'parse_attrs',
            {
                'key': {
                    '$a': {
                        'subkey_attr': {
                            '$a': {'x': 'y'},
                            '$v': 'subkey_extra_attr',
                        },
                    },
                    '$v': 'value',
                },
            },
        ),
        (
            {'key': yt.yson.to_yson_type(None, attributes={'x': 'y'})},
            'parse_json',
            # compatibility null -> attrs
            {'key': {'x': 'y'}},
        ),
        (
            {'key': yt.yson.to_yson_type(None, attributes={'x': 'y'})},
            'parse_attrs',
            {'key': {'$a': {'x': 'y'}, '$v': None}},
        ),
        (
            _YSON_WITH_LIST,
            'parse_yt_value_json',
            {'key': ['string', {'subkey': {'subkey2': 'subvalue'}}]},
        ),
        (None, 'parse_yt_value_json', None),
        (
            _YSON_WITH_LIST,
            'parse_attrs',
            {
                'key': {
                    '$a': {'x': 'y'},
                    '$v': [
                        {'$a': {'x': 'y'}, '$v': 'string'},
                        {
                            '$a': {'x': 'y'},
                            '$v': {
                                'subkey': {
                                    '$a': {'subattr': 'subattrvalue'},
                                    '$v': {'subkey2': 'subvalue'},
                                },
                            },
                        },
                    ],
                },
            },
        ),
        (
            {
                'key': yt.yson.to_yson_type(
                    'string_with_attrs', attributes={'x': 'y'},
                ),
            },
            'parse_value_key',
            {'parsed': 'string_with_attrs'},
        ),
        (
            {'key': 'normal_string'},
            'parse_value_key',
            {'parsed': 'normal_string'},
        ),
        ({'key': 34}, 'parse_value_key', {'parsed': 'unparsed'}),
        (
            {'key': yt.yson.to_yson_type(34, attributes={'x': 'y'})},
            'parse_value_key',
            {'parsed': 'unparsed'},
        ),
    ],
)
@pytest.mark.parametrize(
    # There are 2 different ways in which YT interprets the nulls
    # See details: https://st.yandex-team.ru/YT-13469
    'null_like_empty',
    [
        # Empty yson entity: Yson('#') (inserts by python replication)
        # NTaxi::YT::EValueType_Null in yt-wrapper
        False,
        # Real null
        True,
    ],
)
async def test_lookup_rows_parse_attrs(
        taxi_userver_ytlib_sample,
        yt_apply,
        yt_client,
        input_obj,
        mode_of_get,
        expected_json,
        null_like_empty,
):
    if null_like_empty and input_obj is None:
        yt_client.insert_rows('//home/testsuite/any', [{'id': 'foo'}])
    else:
        yt_client.insert_rows(
            '//home/testsuite/any', [{'id': 'foo', 'value': input_obj}],
        )

    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/any',
            'ids': ['foo'],
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 1
    string = items[0]['value']
    assert json.loads(string) == expected_json, string


async def test_lookup_row_integer_yt_value(
        taxi_userver_ytlib_sample, yt_apply, yt_client,
):
    yt_client.insert_rows(
        '//home/testsuite/any', [{'id': 'foo', 'int_value': 12}],
    )
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/any',
            'ids': ['foo'],
            'mode': 'parse_yt_value_int',
        },
    )
    assert response.json()['items'][0]['value'] == '12'
