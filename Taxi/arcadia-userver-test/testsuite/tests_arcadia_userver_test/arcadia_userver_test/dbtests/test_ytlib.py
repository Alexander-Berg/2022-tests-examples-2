import pytest


@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_ytlib_happy_path(taxi_arcadia_userver_test, yt_apply):
    response = await taxi_arcadia_userver_test.post(
        '/ytlib/smoke-test',
        json={'yt_cluster': 'hahn', 'table': '//home/testsuite/foo'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'id': 'bar', 'value': 'bar'},
            {'id': 'foo', 'value': 'one'},
        ],
    }
