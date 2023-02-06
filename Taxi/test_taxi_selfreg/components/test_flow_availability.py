import pytest

from taxi import pro_app
from testsuite.utils import http

from taxi_selfreg import models
from taxi_selfreg.components import flow_availability
from taxi_selfreg.generated.service.cities_cache import plugin as cities_cache
from taxi_selfreg.generated.service.swagger.models import api
from taxi_selfreg.generated.web import web_context as context_module

TAXIMETER_USER_AGENT = 'Taximeter 9.61 (1234)'
TAXIMETER_APP = pro_app.app_from_user_agent(TAXIMETER_USER_AGENT)

FlowType = models.SelfregFlowType

DEFAULT_FLOWS_ORDERING = flow_availability.DEFAULT_FLOWS_ORDERING


@pytest.mark.config(
    # this enables selfemployed flows (DRIVER_WITH_AUTO/DRIVER_WITHOUT_AUTO)
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Москва'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
    # this enables ONFOOT_COURIER flow
    TAXIMETER_SELFREG_ON_FOOT_ENABLED={'enable': True, 'cities': ['Москва']},
    # this enables selfreg generally
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'expected_flow_list, hiring_types_called',
    [
        pytest.param(
            [],
            0,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='all_flows_disabled.json',
            ),
            id='all flows disabled in config',
        ),
        pytest.param(
            [
                FlowType.DRIVER_WITHOUT_AUTO,
                FlowType.DRIVER_WITH_AUTO,
                FlowType.ONFOOT_COURIER,
                FlowType.EATS_COURIER,
            ],
            1,
            id='no config, use default',
        ),
        pytest.param(
            [
                FlowType.DRIVER_WITHOUT_AUTO,
                FlowType.DRIVER_WITH_AUTO,
                FlowType.ONFOOT_COURIER,
                FlowType.EATS_COURIER,
            ],
            1,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='empty_config.json',
            ),
            id='empty config, use default',
        ),
        pytest.param(
            [
                FlowType.DRIVER_WITHOUT_AUTO,
                FlowType.DRIVER_WITH_AUTO,
                FlowType.ONFOOT_COURIER,
                FlowType.EATS_COURIER,
            ],
            1,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='empty_list_of_flows.json',
            ),
            id='empty list in config, use default',
        ),
        pytest.param(
            [
                FlowType.EATS_COURIER,
                FlowType.ONFOOT_COURIER,
                FlowType.DRIVER_WITH_AUTO,
                FlowType.DRIVER_WITHOUT_AUTO,
            ],
            1,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='reversed_order_flows.json',
            ),
            id='reversed order in config',
        ),
        pytest.param(
            [
                FlowType.ONFOOT_COURIER,
                FlowType.DRIVER_WITHOUT_AUTO,
                FlowType.EATS_COURIER_NATIVE,
            ],
            1,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='some_flows_force_disabled.json',
            ),
            id='some flows force disabled, the rest are ordered by config',
        ),
        pytest.param(
            [
                FlowType.EATS_COURIER,
                FlowType.DRIVER_WITH_AUTO,
                FlowType.DRIVER_WITHOUT_AUTO,
                FlowType.ONFOOT_COURIER,
            ],
            1,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='some_flows_missing.json',
            ),
            id='some flows are missing from config, they use default ordering',
        ),
        pytest.param(
            [FlowType.EATS_COURIER, FlowType.ONFOOT_COURIER],
            0,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='exclude_flows_that_are'
                '_disabled.json',
            ),
            id='exclude flows that are disabled by config, '
            'order flows by config, then order missing flows by default',
        ),
    ],
)
async def test_flow_availability(
        mockserver,
        web_context: context_module.Context,
        mock_hiring_forms_default,
        mock_fleet_parks,
        expected_flow_list,
        hiring_types_called,
):
    mock_hiring_forms_default.set_regions(['Москва'])

    # this enables park flows (DRIVER_WITH_AUTO/DRIVER_WITHOUT_AUTO)
    @mock_fleet_parks('/v1/parks/driver-hirings/selfreg/types')
    async def _hiring_types(request: http.Request):
        return {'types': ['lease', 'private']}

    flows_result = await web_context.flow_availability.get_available_flows(
        cities_cache.City(
            name='Москва',
            lat=55.45,
            lon=37.37,
            country_id='rus',
            has_eats_courier=True,
        ),
        'some_phone',
        False,
        TAXIMETER_APP,
    )
    assert flows_result.available_flows == expected_flow_list
    assert _hiring_types.times_called == hiring_types_called
    assert mock_hiring_forms_default.regions_handler.has_calls


@pytest.mark.config(
    # this enables selfemployed flows (DRIVER_WITH_AUTO/DRIVER_WITHOUT_AUTO)
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Москва'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
    # this enables selfreg generally
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'check_existing_se,phone,fns_replica_response,has_selfemployed',
    [
        pytest.param(False, 'some_phone', None, True, id='no need to check'),
        pytest.param(False, None, None, True, id='no need to check, no phone'),
        pytest.param(
            True,
            'some_phone',
            'selfemployed_fns_replica_has_profile.json',
            False,
            id='do check, has profile',
        ),
        pytest.param(
            True,
            'some_phone',
            'selfemployed_fns_replica_has_not_profile.json',
            True,
            id='do check, no profile',
        ),
        pytest.param(
            True,
            None,
            'selfemployed_fns_replica_has_profile.json',
            True,
            id='no phone',
        ),
    ],
)
async def test_existing_self_employment(
        mockserver,
        web_context: context_module.Context,
        mock_hiring_forms_default,
        load_json,
        mock_fleet_parks,
        mock_selfemployed_fns_replica,
        check_existing_se,
        phone,
        fns_replica_response,
        has_selfemployed,
):
    mock_hiring_forms_default.set_regions(['Москва'])

    # this enables park flows (DRIVER_WITH_AUTO/DRIVER_WITHOUT_AUTO)
    @mock_fleet_parks('/v1/parks/driver-hirings/selfreg/types')
    async def _hiring_types(request: http.Request):
        return {'types': ['lease', 'private']}

    @mock_selfemployed_fns_replica('/v1/profiles/retrieve-by-phone')
    async def _fns_replica_retrieve_by_phone(request: http.Request):
        return load_json(fns_replica_response)

    flows_result = await web_context.flow_availability.get_available_flows(
        cities_cache.City(
            name='Москва',
            lat=55.45,
            lon=37.37,
            country_id='rus',
            has_eats_courier=True,
        ),
        phone,
        check_existing_se,
        TAXIMETER_APP,
    )
    assert flows_result.has_selfemployed == has_selfemployed
    assert _fns_replica_retrieve_by_phone.times_called == int(
        check_existing_se and phone is not None,
    )


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'gambling_policy, expect_flows',
    [
        pytest.param(
            'use-sf-gambling',
            [FlowType.DRIVER_WITH_AUTO],
            marks=pytest.mark.client_experiments3(
                file_with_default_response='use_sf_gambling.json',
            ),
        ),
        pytest.param(
            'use-sf-gambling-compare',
            [FlowType.DRIVER_WITH_AUTO],
            marks=pytest.mark.client_experiments3(
                file_with_default_response='use_sf_gambling_compare.json',
            ),
        ),
        pytest.param(
            'use-old-gambling',
            [FlowType.DRIVER_WITHOUT_AUTO],
            marks=pytest.mark.client_experiments3(
                file_with_default_response='use_old_gambling.json',
            ),
        ),
        pytest.param(
            'use-old-gambling-compare',
            [FlowType.DRIVER_WITHOUT_AUTO],
            marks=pytest.mark.client_experiments3(
                file_with_default_response='use_old_gambling_compare.json',
            ),
        ),
    ],
)
async def test_flow_availability_sf(
        web_context: context_module.Context,
        patch,
        mock_hiring_forms_default,
        mock_fleet_parks,
        gambling_policy,
        expect_flows,
):
    @mock_fleet_parks('/v1/parks/driver-hirings/selfreg/types')
    async def _hiring_types(request: http.Request):
        return {'types': ['lease']}

    @patch(
        'taxi_selfreg.components.sf_park_gambling.Component.get_driver_parks',
    )
    async def _get_driver_parks(*, is_rent, **kwargs):
        if not is_rent:
            return [
                api.ParksChoice(
                    address='',
                    contact_phones=[],
                    name='some park',
                    park_id='db_id',
                ),
            ]
        return []

    flows_result = await web_context.flow_availability.get_available_flows(
        cities_cache.City(
            name='Москва',
            lat=55.45,
            lon=37.37,
            country_id='rus',
            has_eats_courier=False,
        ),
        'some_phone',
        False,
        TAXIMETER_APP,
    )
    assert flows_result.available_flows == expect_flows
    assert _hiring_types.has_calls == (
        gambling_policy
        in [
            'use-old-gambling',
            'use-old-gambling-compare',
            'use-sf-gambling-compare',
        ]
    )
    assert mock_hiring_forms_default.regions_handler.times_called == 1
