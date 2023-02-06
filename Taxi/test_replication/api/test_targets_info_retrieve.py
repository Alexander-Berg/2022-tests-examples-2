import json

import pytest


@pytest.mark.parametrize(
    'input_request,expected_status,expected_response',
    [
        (
            {'target_names': ['test_errors_rule_struct_2', 'test_rule_bson']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_errors_rule_struct_2',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//allowed/unittests/data/test/test_struct_2'
                            ),
                        },
                    },
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_rule_bson',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/test/test_bson'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['test_rule_external']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_rule_external',
                        'target_type': 'ext',
                        'ext_state': {},
                    },
                ],
            },
        ),
        (
            {
                'target_names': [
                    'test_sharded_mongo_struct',
                    'test_rule_external_2',
                ],
            },
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'enabled',
                            'last_replicated_datetime': (
                                '2020-01-01T18:00:00+03:00'
                            ),
                        },
                        'target_name': 'test_rule_external_2',
                        'target_type': 'ext',
                        'ext_state': {
                            'last_replicated': '2020-01-01T15:00:00',
                            'last_sync_date': '2018-11-14T07:00:00+03:00',
                        },
                    },
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_sharded_mongo_struct',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-man',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-vla',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/'
                                'test/test_struct_sharded_mongo'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {
                'target_names': ['test_sharded_mongo_struct'],
                'target_types': ['ext'],
            },
            200,
            {'target_info': []},
        ),
        (
            {
                'target_names': ['test_sharded_mongo_struct'],
                'target_types': ['ext', 'yt'],
            },
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_sharded_mongo_struct',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-man',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-vla',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/'
                                'test/test_struct_sharded_mongo'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['test_sharded_mongo_struct']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'test_sharded_mongo_struct',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-man',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'seneca-vla',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/'
                                'test/test_struct_sharded_mongo'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['test_rule']},
            200,
            {'target_info': []},  # not found any target
        ),
        (
            {'target_names': ['test_rule', 'test_rule_struct']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'enabled',
                            'last_replicated_datetime': (
                                '2018-11-13T15:00:00+03:00'
                            ),
                        },
                        'target_name': 'test_rule_struct',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'last_replicated': '2018-11-13T15:00:00',
                                    'status': 'enabled',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'last_replicated': '2018-11-13T12:00:00',
                                    'last_sync_date': (
                                        '2018-11-14T07:00:00+03:00'
                                    ),
                                    'status': 'enabled',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/test/test_struct'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_types': ['yt', 'fail']},
            404,
            {
                'code': 'state-targets_info-retrieve-error',
                'message': '[\'fail\'] are incorrect target types',
            },
        ),
        ({}, 200, None),  # get all test rules
        (
            {'target_names': ['basic_source_postgres_sequence']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {'field': 'id', 'type': 'int'},
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'basic_source_postgres_sequence',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/'
                                'postgres/basic_source_postgres_sequence'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['partitioning_slice']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {
                            'overall_status': 'not_initialized',
                        },
                        'target_name': 'partitioning_slice',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'status': 'not_initialized',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/'
                                'targets_retrieve/partitioning'
                            ),
                            'partitions': [
                                '2020-06_2020-10',
                                '2020-01_2020-05',
                            ],
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['api_replicate_by']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {
                            'iteration_field': {
                                'field': 'updated',
                                'type': 'datetime',
                            },
                            'replication_type': 'queue',
                        },
                        'replication_state': {'overall_status': 'mixed'},
                        'target_name': 'api_replicate_by',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                {
                                    'cluster_name': 'hahn',
                                    'last_replicated': '2020-01-01T15:00:00',
                                    'status': 'enabled',
                                },
                            ],
                            'full_path': (
                                '//home/taxi/unittests/test/api/test_struct'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            {'target_names': ['test_api_basestamp_struct']},
            200,
            {
                'target_info': [
                    {
                        'replication_settings': {'replication_type': 'queue'},
                        'replication_state': {'overall_status': 'mixed'},
                        'target_name': 'test_api_basestamp_struct',
                        'target_type': 'yt',
                        'yt_state': {
                            'clusters_states': [
                                {
                                    'cluster_name': 'arni',
                                    'status': 'not_initialized',
                                },
                                # last_ts is not valid base_last_stamp
                                {'cluster_name': 'hahn', 'status': 'enabled'},
                            ],
                            'full_path': (
                                '//home/taxi/unittests/test/api/test_struct'
                            ),
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2020-07-29T10:20:00+0000')
async def test_targets_info_retrieve(
        replication_client, input_request, expected_status, expected_response,
):
    response = await replication_client.post(
        '/v3/state/targets_info/retrieve', data=json.dumps(input_request),
    )
    assert response.status == expected_status, await response.text()
    if expected_response is not None:
        assert await response.json() == expected_response
