import pytest


@pytest.fixture(autouse=True)
def mock_yt_replications(mockserver):
    @mockserver.json_handler('/replication/state/all_yt_target_info')
    def mock_replication(request):
        return {
            'targets_info': [
                {
                    'table_path': 'private/mongo/bson/orders',
                    'target_names': [
                        'orders_bson_runtime',
                        'orders_bson_map_reduce',
                    ],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'private/mongo/bson/order_proc',
                    'target_names': [
                        'order_proc_order_id_index',
                        'order_proc_bson_map_reduce',
                    ],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'private/mongo/bson/mph_results',
                    'target_names': ['mph_results'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': (
                        'private/mongo/bson/subvention_reasons_by_order_id'
                    ),
                    'target_names': ['subvention_reasons_by_order_id'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
            ],
        }
