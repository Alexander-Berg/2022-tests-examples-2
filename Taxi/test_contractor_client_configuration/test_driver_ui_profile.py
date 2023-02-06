import pytest

from tests_contractor_state.test_contractor_client_configuration import consts


@pytest.mark.experiments3(
    name='experiment_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'driver_mode_type',
                    'set': ['display_mode'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=False,
)
async def test_driver_mode_type_kwarg(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200
    experiments = response.json()['typed_experiments']['items']
    assert experiments['experiment_name']['key'] == 'val'


@pytest.mark.experiments3(
    name='experiment_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'display_profile',
                    'set': ['display_profile'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=False,
)
async def test_display_profile_kwarg(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200
    experiments = response.json()['typed_experiments']['items']
    assert experiments['experiment_name']['key'] == 'val'


@pytest.mark.config(CONTRACTOR_STATE_DEFAULT_UI_MODE_CONCERN='urgent')
async def test_requested_concern(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        assert request.query['concern'] == 'cached'
        return {
            'display_mode': 'display_mode',
            'display_profile': 'display_profile',
        }

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={'ui_mode_concern': 'cached'},
    )
    assert response.status_code == 200


@pytest.mark.config(CONTRACTOR_STATE_DEFAULT_UI_MODE_CONCERN='urgent')
async def test_default_cocnern(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        assert request.query['concern'] == 'urgent'
        return {
            'display_mode': 'display_mode',
            'display_profile': 'display_profile',
        }

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200


@pytest.mark.config(
    CONTRACTOR_STATE_FALLBACK_ON_DRIVER_UI_TAGS={
        'condition': 'always',
        'rules': [
            {
                'display_mode': 'display_mode',
                'display_profile': 'display_profile',
                'tag': 'tag1',
            },
        ],
    },
)
@pytest.mark.experiments3(
    name='experiment_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'driver_mode_type',
                    'set': ['display_mode'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=False,
)
async def test_fallback_always_and_rule_matched(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        return mockserver.make_response(status=500)

    driver_tags_mocks.set_tags_info(
        'park_id', 'driver_profile_id', ['tag1', 'tag2'],
    )

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    experiments = response.json()['typed_experiments']['items']
    assert experiments['experiment_name']['key'] == 'val'


@pytest.mark.config(
    CONTRACTOR_STATE_FALLBACK_ON_DRIVER_UI_TAGS={
        'condition': 'always',
        'rules': [
            {
                'display_mode': 'display_mode',
                'display_profile': 'display_profile',
                'tag': 'tag999',
            },
        ],
    },
)
async def test_fallback_always_and_rule_not_matched(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        return mockserver.make_response(status=500)

    driver_tags_mocks.set_tags_info(
        'park_id', 'driver_profile_id', ['tag1', 'tag2'],
    )

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 500


@pytest.mark.config(
    CONTRACTOR_STATE_FALLBACK_ON_DRIVER_UI_TAGS={
        'condition': 'only_cached',
        'rules': [
            {
                'display_mode': 'orders',
                'display_profile': 'uberdriver',
                'tag': 'uberdriver',
            },
        ],
    },
)
async def test_fallback_only_cached_and_ui_mode_concern_urgent(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        return mockserver.make_response(status=500)

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={'ui_mode_concern': 'invalidate'},
    )
    assert response.status_code == 500


@pytest.mark.config(
    CONTRACTOR_STATE_FALLBACK_ON_DRIVER_UI_TAGS={
        'condition': 'never',
        'rules': [
            {
                'display_mode': 'orders',
                'display_profile': 'uberdriver',
                'tag': 'uberdriver',
            },
        ],
    },
)
async def test_fallback_never(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _v1_mode(request):
        return mockserver.make_response(status=500)

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 500
