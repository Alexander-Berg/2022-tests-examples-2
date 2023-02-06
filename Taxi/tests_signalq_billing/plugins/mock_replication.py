# encoding=utf-8
import pytest


COMMON_TARGET_FIELDS = {
    'target_type': 'yt',
    'replication_state': {'overall_status': 'enabled'},
    'replication_settings': {
        'replication_type': 'queue',
        'iteration_field': {'type': 'datetime', 'field': 'updated_at'},
    },
}

ARNOLD_CLUSTER_STATE_ACTUAL = {
    'cluster_name': 'arnold',
    'status': 'enabled',
    'last_sync_date': '2021-10-12T13:45:28.243000+03:00',
    'last_replicated': '2021-10-12T15:43:43.216000',
}

ARNOLD_CLUSTER_STATE_OLD = {
    'cluster_name': 'arnold',
    'status': 'enabled',
    'last_sync_date': '2021-08-12T13:45:28.243000+03:00',
    'last_replicated': '2021-08-12T15:43:43.216000',
}

HAHN_CLUSTER_STATE_ACTUAL = {
    'cluster_name': 'hahn',
    'status': 'disabled',
    'last_sync_date': '2021-10-12T13:45:28.243000+03:00',
    'last_replicated': '2021-10-12T15:43:43.216000',
}

HAHN_CLUSTER_STATE_OLD = {
    'cluster_name': 'hahn',
    'status': 'disabled',
    'last_sync_date': '2021-09-23T13:45:28.250000+03:00',
    'last_replicated': '2021-08-26T15:43:43.216000',
}


@pytest.fixture(name='replication', autouse=True)
def _mock_replication(mockserver):
    class ReplicationContext:
        def __init__(self):
            self.response = {
                'target_info': [
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': (
                            'signal_device_api_park_device_profiles'
                        ),
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/park_device_profiles',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [
                                HAHN_CLUSTER_STATE_OLD,
                                ARNOLD_CLUSTER_STATE_ACTUAL,
                            ],
                        },
                    },
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': 'signal_device_api_devices',
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/devices',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [
                                HAHN_CLUSTER_STATE_ACTUAL,
                                ARNOLD_CLUSTER_STATE_ACTUAL,
                            ],
                        },
                    },
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': 'signal_device_api_status_history',
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/status_history',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [
                                HAHN_CLUSTER_STATE_ACTUAL,
                                ARNOLD_CLUSTER_STATE_ACTUAL,
                            ],
                        },
                    },
                ],
            }

        def set_no_active_clusters(self):
            self.response = {
                'target_info': [
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': (
                            'signal_device_api_park_device_profiles'
                        ),
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/park_device_profiles',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [  # Remove here arnold
                                HAHN_CLUSTER_STATE_OLD,
                            ],
                        },
                    },
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': 'signal_device_api_devices',
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/devices',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [
                                HAHN_CLUSTER_STATE_OLD,
                                ARNOLD_CLUSTER_STATE_ACTUAL,
                            ],
                        },
                    },
                    {
                        **COMMON_TARGET_FIELDS,
                        'target_name': 'signal_device_api_status_history',
                        'yt_state': {
                            'full_path': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/status_history',  # noqa: E501 pylint: disable=line-too-long
                            'clusters_states': [
                                HAHN_CLUSTER_STATE_OLD,
                                ARNOLD_CLUSTER_STATE_ACTUAL,
                            ],
                        },
                    },
                ],
            }

    context = ReplicationContext()

    @mockserver.json_handler('/replication/v3/state/targets_info/retrieve')
    def _mock_v3_state(request):
        return context.response

    return context
