import bson
import pytest
import yt.yson


@pytest.fixture
def yt_client_response_lookup(mockserver):
    def _persorm_handler(order_id):
        doc = {b'doc': bson.BSON.encode({'_id': order_id})}
        response = yt.yson.dumps(doc, yson_format='binary', encoding=None)
        return mockserver.make_response(
            response, content_type='application/x-yt-yson-binary',
        )

    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    def lookup_rows_test(request):
        return _persorm_handler('test_order_id')

    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_repl(request):
        return _persorm_handler('repl_order_id')


def dummy_replication(mockserver, yt_test_delay, yt_repl_delay):
    @mockserver.json_handler('/replication/state/all_yt_target_info')
    def mock_replication(request):
        return {
            'targets_info': [
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['orders_bson_runtime'],
                    'clients_delays': [
                        {
                            'client_name': 'yt-test',
                            'current_delay': yt_test_delay,
                        },
                        {
                            'client_name': 'yt-repl',
                            'current_delay': yt_repl_delay,
                        },
                    ],
                },
            ],
        }


def check_response(response, expected_response_id):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {
        'source': 'yt',
        'doc': {'_id': expected_response_id},
    }


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_order_yt_test(
        taxi_archive_api, yt_client_response_lookup, mockserver,
):
    dummy_replication(mockserver, 0, 100000)
    response = taxi_archive_api.post('archive/order', json={'id': 'order_id'})
    check_response(response, 'test_order_id')


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T14:57:00Z')
def test_correct_order_yt_repl(
        taxi_archive_api, yt_client_response_lookup, mockserver,
):
    dummy_replication(mockserver, 100000, 0)
    response = taxi_archive_api.post('archive/order', json={'id': 'order_id'})
    check_response(response, 'repl_order_id')


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_order_none(
        taxi_archive_api, yt_client_response_lookup, mockserver,
):
    dummy_replication(mockserver, 100000, 100000)
    response = taxi_archive_api.post('archive/order', json={'id': 'order_id'})
    assert response.status_code == 503
