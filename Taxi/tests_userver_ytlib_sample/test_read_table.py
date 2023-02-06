import pytest


@pytest.mark.parametrize('mode_of_get', ['by_index', 'by_name'])
@pytest.mark.yt(
    schemas=['yt_static_foo_schema.yaml'],
    static_table_data=['yt_static_foo.yaml'],
)
async def test_read_table(taxi_userver_ytlib_sample, yt_apply, mode_of_get):
    response = await taxi_userver_ytlib_sample.post(
        'ytlib/read-table',
        json={
            'yt_cluster': 'hahn',
            'table': '//home/testsuite/static/foo',
            'mode': mode_of_get,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'id': 'bar', 'value': 'static1'},
            {'id': 'foo', 'value': 'static2'},
        ],
    }
