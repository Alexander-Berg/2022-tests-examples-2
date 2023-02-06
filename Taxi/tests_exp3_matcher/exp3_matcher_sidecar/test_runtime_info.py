import pytest


@pytest.fixture(name='mock_runtime_info', autouse=True)
def _create_handle(mockserver):
    @mockserver.json_handler(
        '/taxi-exp-uservices/v1/consumers/kwargs/',
    )  # runtime info handler
    def _mock_runtime_info(request):
        assert (
            request.json['consumer'] == 'test_consumer'
            or request.json['consumer'] == 'another_consumer'
        )
        if request.json['consumer'] == 'another_consumer':
            assert request.json['namespace'] == 'market'
        else:
            assert 'namespace' not in request.json
        assert (
            sorted(request.json['kwargs'], key=lambda x: x['name'])
            == sorted(
                [
                    {
                        'is_mandatory': False,
                        'name': 'is_prestable',
                        'type': 'bool',
                    },
                    {
                        'is_mandatory': False,
                        'name': 'datacenter',
                        'type': 'string',
                    },
                    {
                        'is_mandatory': False,
                        'name': 'request_timestamp',
                        'type': 'int',
                    },
                    {
                        'is_mandatory': False,
                        'name': 'request_timestamp_minutes',
                        'type': 'int',
                    },
                    {
                        'is_mandatory': False,
                        'name': 'service',
                        'type': 'string',
                    },
                    {
                        'is_mandatory': False,
                        'name': 'consumer',
                        'type': 'string',
                    },
                ],
                key=lambda x: x['name'],
            )
        )
        assert set(request.json['metadata']['supported_features']) == {
            'match-statistics',
            'merge-by-tag',
            'trait-tags',
            'segmentation-predicate',
            # 'matching-logs',
        }
        return {}

    return _mock_runtime_info


def patch_for_sidecar():
    def _patch(config, config_vars):
        config_vars['experiments3_consumers'] = ['test_consumer']
        config_vars['is_prestable'] = True
        config['components_manager']['components']['kwargs-controller'][
            'use-sidecar-builder'
        ] = True
        config['components_manager']['components']['kwargs-controller'][
            'is-prestable'
        ] = '$is_prestable'
        config['components_manager']['components']['kwargs-controller'][
            'consumers'
        ] = ['another_consumer']
        config['components_manager']['components']['kwargs-controller'][
            'consumers-namespace'
        ] = 'market'
        config['components_manager']['components']['kwargs-controller'][
            'default-kwargs'
        ] = (
            [
                {'name': 'datacenter', 'type': 'string', 'value': 'sas'},
                {'name': 'service', 'type': 'string', 'value': 'planner'},
            ]
        )

    return pytest.mark.uservice_oneshot(config_hooks=[_patch])


@pytest.mark.experiments3(
    name='test_runtime_info',
    consumers=['test_consumer'],
    clauses=[
        {
            'title': 'some_kwarg + dc',
            'value': {'key': 230},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'some_kwarg',
                                'arg_type': 'string',
                                'value': 'some_value',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'datacenter',
                                'arg_type': 'string',
                                'value': 'sas',
                            },
                        },
                    ],
                },
            },
        },
    ],
    default_value={'key': 228},
    trait_tags=['prestable'],
)
@patch_for_sidecar()
async def test_runtime_info_on_start_sidecar(
        taxi_exp3_matcher, mock_runtime_info, testpoint,
):
    @testpoint('exp3::runtime_info_sent')
    def runtime_info_sent(data):
        pass

    request = {
        'consumer': 'test_consumer',
        'args': [
            {'name': 'some_kwarg', 'type': 'string', 'value': 'some_value'},
        ],
    }
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    assert response.json() == {
        'items': [{'name': 'test_runtime_info', 'value': {'key': 230}}],
        'version': 1,
    }

    await runtime_info_sent.wait_call()
    assert mock_runtime_info.times_called == 2
