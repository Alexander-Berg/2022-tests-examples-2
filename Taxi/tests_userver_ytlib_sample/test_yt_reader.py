import pytest


@pytest.mark.parametrize(
    'target_name, success',
    [
        ('repl-target-rt', True),
        ('repl-target-mr', True),
        ('repl-target-both', False),
        ('undefined', False),
    ],
)
@pytest.mark.parametrize('parse_mode', ['ytlib', 'json_generated_model'])
@pytest.mark.yt(dyn_table_data=['yt_foo.yaml'])
async def test_lookup_rows(
        taxi_userver_ytlib_sample, yt_apply, target_name, success, parse_mode,
):
    response = await taxi_userver_ytlib_sample.post(
        'yt-reader/lookup-rows',
        json={'target_name': target_name, 'parse_mode': parse_mode},
    )
    _check_response(response, success)


@pytest.mark.parametrize(
    'target_names, success',
    [
        (['repl-target-rt', 'repl-target-rt'], True),
        (['repl-target-mr', 'repl-target-mr'], True),
        (['repl-target-rt', 'repl-target-both'], True),
        (['repl-target-rt', 'repl-target-mr'], False),
        (['repl-target-both', 'repl-target-both'], False),
        (['repl-target-rt', 'undefined'], False),
    ],
)
@pytest.mark.parametrize('parse_mode', ['ytlib', 'json_generated_model'])
@pytest.mark.yt(schemas=['yt_foo_schema.yaml'], dyn_table_data=['yt_foo.yaml'])
async def test_select_rows(
        taxi_userver_ytlib_sample, yt_apply, target_names, success, parse_mode,
):
    response = await taxi_userver_ytlib_sample.post(
        'yt-reader/select-rows',
        json={'target_names': target_names, 'parse_mode': parse_mode},
    )
    _check_response(response, success)


def _check_response(response, success):
    if success:
        assert response.status_code == 200
        assert response.json() == {
            'items': [
                {'id': 'bar', 'value': 'def'},
                {'id': 'foo', 'value': 'abc'},
            ],
        }
    else:
        assert response.status_code == 500


@pytest.mark.yt(dyn_table_data=['yt_foo.yaml'])
async def test_lookup_rows_raw(taxi_userver_ytlib_sample, yt_apply):
    response = await taxi_userver_ytlib_sample.post(
        'yt-reader/lookup-rows-raw', json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'id': 'foo',
                'renamed_value': {
                    'updated_ts': '2021-02-24T13:58:35.503107+00:00',
                },
            },
        ],
    }
