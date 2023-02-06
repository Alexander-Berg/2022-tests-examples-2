import json

import pytest


@pytest.mark.parametrize(
    'mode_of_get', ['by_index', 'by_name', 'by_name_reverse_query'],
)
@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_select_rows(taxi_userver_ytlib_sample, yt_apply, mode_of_get):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/select-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/foo',
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'id': 'bar', 'value': 'bar'},
            {'id': 'foo', 'value': 'one'},
        ],
    }


@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_select_rows_try_get_any(taxi_userver_ytlib_sample, yt_apply):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/select-rows',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/raw',
            'mode': 'try_get_any',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    values = {
        val['id']: json.loads(val['value']) for val in response_json['items']
    }

    assert values == {
        'bar': None,
        'foo': {'$a': {'attr': 'attrkey'}, '$v': 'value'},
    }
