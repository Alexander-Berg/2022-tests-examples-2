import pytest


SERVICE = 'eats_fts'
PREFIX = 1


@pytest.mark.yt(schemas=['yt_schema.yaml'], static_table_data=['yt_data.yaml'])
async def test_saas_bulk_delete_from_yt(yt_apply, mockserver, stq_runner):
    """
    Проверяем, что stq задача saas_batch_delete_from_yt
    удаляет документы с url перечисленными в таблице
    """

    urls = frozenset(
        ['/place/items/1', '/place/items/2', '/place/categories/3'],
    )

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        payload = request.json
        assert payload['action'] == 'delete'
        assert payload['docs'][0]['url'] in urls
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await stq_runner.eats_full_text_search_indexer_saas_bulk_delete_from_yt.call(  # noqa
        task_id='id_1',
        kwargs={
            'saas_settings': {
                'service_alias': SERVICE,
                'prefix': PREFIX,
                'batch_size': 2,
            },
            'yt_settings': {
                'cluster': 'testsuite',
                'table_path': '//home/table',
                'batch_size': 1,
                'retries': 2,
            },
        },
    )

    assert saas_push.times_called == len(urls)
