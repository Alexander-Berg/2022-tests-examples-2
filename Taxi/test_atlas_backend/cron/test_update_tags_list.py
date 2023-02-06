import pytest

from atlas_backend.generated.cron import run_cron


async def _ch_result_gen():
    all_results = [
        [('new_tag1',), ('new_tag2',), ('tag3',)],
        [('utag3',), ('utag4',)],
        [('new_tag1',), ('tag4',)],
    ]
    for result in all_results:
        yield result


@pytest.mark.config(
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {'etl.update_tags_list': {'run_permission': True}},
    },
)
async def test_update_tags_list(
        clickhouse_client_mock, web_app_client, patch, db,
):
    ch_result_gen = _ch_result_gen()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        return await ch_result_gen.__anext__()

    await run_cron.main(
        ['atlas_backend.crontasks.update_tags_list', '-t', '0'],  # noqa: E501
    )

    response = await web_app_client.get('/api/v1/tags')
    assert response.status == 200

    content = await response.json()
    expected = [
        'new_tag1',
        'new_tag2',
        'qqq',
        'tag1',
        'tag2',
        'tag3',
        'tag4',
        'utag1',
        'utag3',
        'utag4',
    ]
    assert content == expected
