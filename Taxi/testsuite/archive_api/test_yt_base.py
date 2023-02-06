import pytest


@pytest.mark.parametrize(
    'archive_handler, archive_data',
    [
        ('archive/order', {'id': 'order_id'}),
        ('archive/orders', {'ids': ['order_id']}),
        ('archive/orders/restore', {'id': 'order_id'}),
        ('archive/order_proc/restore', {'id': 'order_id'}),
        ('archive/mph_results/restore', {'id': 'order_id'}),
        ('archive/subvention_reasons/restore', {'id': 'order_id'}),
        (
            'v1/yt/lookup_rows',
            {
                'query': [{'id': 'order_id'}],
                'replication_rule': {'name': 'orders_bson_map_reduce'},
            },
        ),
        (
            'v1/yt/select_rows',
            {
                'query': {'query_string': '* FROM [//tmp] LIMIT 1'},
                'replication_rules': [{'name': 'orders_bson_map_reduce'}],
            },
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_yt_no_hosts(
        taxi_archive_api, mockserver, now, archive_handler, archive_data,
):
    @mockserver.json_handler('/yt/yt-test/hosts')
    @mockserver.json_handler('/yt/yt-repl/hosts')
    def get_hosts(request):
        return []

    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def get_data(request):
        assert False

    taxi_archive_api.tests_control(now, invalidate_caches=True)

    response = taxi_archive_api.post(archive_handler, json=archive_data)
    assert response.status_code == 503


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
def test_yt_too_many_hosts(taxi_archive_api, mockserver):
    @mockserver.json_handler('/yt/yt-test/hosts')
    def get_hosts(request):
        return []

    @mockserver.json_handler('/yt/yt-repl/hosts')
    def get_hosts2(request):
        return [
            mockserver.url('/yt/yt-repl-1'),
            mockserver.url('/yt/yt-repl-2'),
            mockserver.url('/yt/yt-repl-3'),
            mockserver.url('/yt/yt-repl-4'),
            mockserver.url('/yt/yt-repl-5'),
            mockserver.url('/yt/yt-repl-6'),
            mockserver.url('/yt/yt-repl-7'),
        ]

    @mockserver.json_handler('/yt/yt-repl-1/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl-2/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl-3/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl-4/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl-5/api/v3/lookup_rows')
    def get_data_unavailable(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/yt/yt-repl-6/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl-7/api/v3/lookup_rows')
    def get_data_unused(request):
        assert False

    taxi_archive_api.tests_control()
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'order_id'}],
            'replication_rule': {'name': 'orders_bson_map_reduce'},
        },
    )
    assert response.status_code == 500
