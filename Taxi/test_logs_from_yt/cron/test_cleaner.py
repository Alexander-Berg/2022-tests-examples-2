import pytest


@pytest.mark.config(LOGS_ELASTIC_HOSTS=[{'$mockserver': '/elasticsearch'}])
async def test_errors(cron_runner, mockserver, testpoint):
    @testpoint('cleaner_bulk_index_error')
    def _bulk_index_error(data):
        assert 'no such index [yandex-taxi-archive]' in data

    @mockserver.json_handler('/elasticsearch/')
    def _info_mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'version': {'number': '7.16.2', 'build_flavor': 'default'},
                'tagline': 'You Know, for Search',
            },
            headers={'x-elastic-product': 'Elasticsearch'},
        )

    @mockserver.json_handler(
        '/elasticsearch/yandex-taxi-archive/_search', prefix=True,
    )
    def _search_mock(request):
        return {
            '_scroll_id': 'abc',
            'took': 4,
            'timed_out': False,
            '_shards': {
                'total': 1,
                'successful': 1,
                'skipped': 0,
                'failed': 0,
            },
            'hits': {
                'total': {'value': 0, 'relation': 'eq'},
                'max_score': None,
                'hits': [{'_id': '1', '_index': 'yandex-taxi-archive'}],
            },
        }

    @mockserver.json_handler('/elasticsearch/_search/scroll', prefix=True)
    def _search_scroll_mock(request):
        return {'hits': {'hits': []}}

    @mockserver.json_handler('/elasticsearch/_bulk', prefix=True)
    def _bulk_mock(request):
        return {
            'took': 0,
            'errors': True,
            'items': [
                {
                    'delete': {
                        '_index': 'yandex-taxi-archive',
                        '_type': '_doc',
                        '_id': '1',
                        'status': 404,
                        'error': {
                            'type': 'index_not_found_exception',
                            'reason': 'no such index [yandex-taxi-archive]',
                            'resource.type': 'index_expression',
                            'resource.id': 'yandex-taxi-archive',
                            'index_uuid': '_na_',
                            'index': 'yandex-taxi-archive',
                        },
                    },
                },
            ],
        }

    with pytest.raises(RuntimeError):
        await cron_runner.cleaner()

    assert _bulk_index_error.times_called == 1
    assert _info_mock.times_called == 2
    assert _search_mock.times_called == 1
    assert _search_scroll_mock.times_called == 1
    assert _bulk_mock.times_called == 1
