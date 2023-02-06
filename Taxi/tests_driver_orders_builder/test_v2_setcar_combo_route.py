import json

import pytest


MOCKED_NOW = '2021-10-20T09:00:00+03:00'

ALWAYS_TRUE = {'predicate': {'type': 'true'}, 'enabled': True}

DEFAULT_PLATFORM_CLEANUP_SETTINGS = {
    'create': {
        'optional_fields': ['internal'],
        'required_fields': ['ui'],
        'required_experiments': ['direct_assignment'],
    },
}

DEFAULT_CLEAN_VALUE = {
    'push_cleanup_enabled': True,
    'push_cleanup_settings': {'android': DEFAULT_PLATFORM_CLEANUP_SETTINGS},
}

# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        taximeter_backend_driver_messages={
            'notification.key': {'ru': 'notify'},
        },
    ),
    pytest.mark.experiments3(
        match=ALWAYS_TRUE,
        is_config=True,
        name='driver_orders_builder_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={
            'enable_requirements_rebuild': True,
            'enable_candidate_meta_request': True,
        },
    ),
    pytest.mark.experiments3(
        match=ALWAYS_TRUE,
        is_config=True,
        name='driver_orders_builder_push_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[
            {
                'title': 'for_combo',
                'predicate': {
                    'init': {'arg_name': 'is_combo'},
                    'type': 'bool',
                },
                'value': DEFAULT_CLEAN_VALUE,
            },
        ],
        default_value={
            'push_cleanup_enabled': False,
            'push_cleanup_settings': {
                'android': DEFAULT_PLATFORM_CLEANUP_SETTINGS,
            },
        },
    ),
]


@pytest.mark.parametrize('testcase', ['first_order', 'second_order'])
@pytest.mark.now(MOCKED_NOW)
async def test_base(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        mockserver,
        setcar_create_params,
        testcase,
        order_proc,
):
    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _mock_candidate_meta(request):
        return {'metadata': load_json(f'{testcase}_candidate_meta.json')}

    order_proc.set_file(load_json, f'{testcase}_order_core_response.json')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    response_json = response.json()
    setcar = response_json['setcar']
    assert setcar['internal'] == load_json(f'{testcase}_setcar_internal.json')
    assert ('internal' in response_json['setcar_push']) == (
        testcase == 'second_order'
    )

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar['id'])
    redis_dict = json.loads(redis_str)
    assert redis_dict['internal'] == setcar['internal']
