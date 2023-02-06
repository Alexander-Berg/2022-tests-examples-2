# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest


from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.parametrize(
    'payload, expected_response',
    [
        pytest.param(
            helpers.build_payload(
                position=consts.INVALID_POSITION, empty_services=True,
            ),
            consts.EMPTY_RESPONSE,
            id='empty services, exp. is not available, zone is incorrect',
        ),
        pytest.param(
            helpers.build_payload(
                position=consts.INVALID_POSITION, empty_services=True,
            ),
            consts.EMPTY_RESPONSE,
            marks=pytest.mark.experiments3(
                filename='exp3_superapp_availability.json',
            ),
            id='empty services, experiment is available, zone is incorrect',
        ),
        pytest.param(
            helpers.build_payload(position=consts.INVALID_POSITION),
            consts.EMPTY_RESPONSE,
            marks=pytest.mark.experiments3(
                filename='exp3_superapp_availability.json',
            ),
            id='all services, experiment is available, zone is incorrect',
        ),
        pytest.param(
            helpers.build_payload(position=consts.INVALID_POSITION),
            helpers.taxi_ok_response(zone_name=None),
            marks=pytest.mark.experiments3(
                filename='exp3_superapp_availability_force_taxi_mode.json',
            ),
            id='empty services, force taxi mode',
        ),
        pytest.param(
            helpers.build_payload(empty_services=True),
            helpers.taxi_ok_response(),
            id='empty services, experiment is not available, zone is correct',
        ),
        pytest.param(
            helpers.build_payload(
                empty_services=True, fields=['geobase_city_id'],
            ),
            helpers.taxi_ok_response(geobase_city_id=213),
            marks=pytest.mark.experiments3(
                filename='exp3_superapp_availability.json',
            ),
            id='empty services, experiment is available, zone is correct',
        ),
    ],
)
async def test_services_available(
        taxi_superapp_misc, payload, expected_response,
):
    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    (
        'enable_cache, send_cached_exp, language, version, expected_version, '
        'expected_cache_status, expected_value, request_shortcuts'
    ),
    [
        pytest.param(
            True,
            True,
            'ru',
            '0:1:ru',
            '1:1:ru',
            'updated',
            {'xxx': 'yyy'},
            None,
            id='cached and updated',
        ),
        pytest.param(
            True,
            True,
            'ru',
            '1:1:ru',
            None,
            'not_modified',
            None,
            None,
            id='cached with the same version',
        ),
        pytest.param(
            True,
            True,
            'en',
            '1:1:ru',
            '1:1:en',
            'updated',
            {'xxx': 'yyy'},
            None,
            id='cached with different language',
        ),
        pytest.param(
            True,
            True,
            'ru',
            '2:1:ru',
            '1:1:ru',
            'updated',
            {'xxx': 'yyy'},
            None,
            id='cached with greater version than known',
        ),
        pytest.param(
            True,
            False,
            'ru',
            '4:1:ru',
            '1:1:ru',
            'updated',
            {'xxx': 'yyy'},
            None,
            id='request without typed_experiments',
        ),
        pytest.param(
            False,
            True,
            'ru',
            '0:1:ru',
            None,
            'no_cache',
            {'xxx': 'yyy'},
            None,
            id='cache is disabled',
        ),
        pytest.param(
            False,
            True,
            'ru',
            '0:0:ru',
            None,
            'no_cache',
            {'icon': 'big'},
            {'supported_icon_sizes': ['medium', 'big']},
            id='test kwargs',
        ),
    ],
)
async def test_typed_experimets(
        taxi_superapp_misc,
        experiments3,
        enable_cache,
        send_cached_exp,
        language,
        version,
        expected_version,
        expected_cache_status,
        expected_value,
        request_shortcuts,
):
    experiments3.add_experiment(
        name='client_superapp_availability',
        consumers=['client-superapp-misc/availability'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'supported_icon_sizes',
                                    'set_elem_type': 'string',
                                    'value': 'big',
                                },
                                'type': 'contains',
                            },
                            {
                                'init': {
                                    'arg_name': 'locale',
                                    'arg_type': 'string',
                                    'value': 'ru',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'icon': 'big'},
            },
            {'predicate': {'type': 'true'}, 'value': {'xxx': 'yyy'}},
        ],
        default_value={},
        trait_tags=['cache-on-clients'] if enable_cache else [],
    )
    payload = helpers.build_payload(
        empty_services=True, shortcuts=request_shortcuts,
    )
    if send_cached_exp:
        payload['typed_experiments'] = {
            'items': [
                {'name': 'client_superapp_availability', 'version': version},
            ],
        }
    response = await taxi_superapp_misc.post(
        consts.URL, payload, headers={'X-Request-Language': language},
    )
    assert response.status_code == 200

    json_result = response.json()
    expected_item = {
        'cache_status': expected_cache_status,
        'name': 'client_superapp_availability',
    }
    if expected_version:
        expected_item['version'] = expected_version
    if expected_value:
        expected_item['value'] = expected_value
    assert json_result['typed_experiments'] == {
        'items': [expected_item],
        'version': 1,
    }


@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize('eats_available', [True, False])
@pytest.mark.parametrize('grocery_available', [True, False])
async def test_ok_response(
        taxi_superapp_misc, eats_available, grocery_available,
):
    payload = helpers.build_payload(
        eats_available=eats_available, grocery_available=grocery_available,
    )
    expected_json = helpers.ok_response(eats_available, grocery_available)

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'exp_value, expected_additional_modes_params, expected_additional_params',
    [
        (helpers.build_exp_value(), {}, {}),
        (
            helpers.build_exp_value(
                hide_strategy='some_hide_strategy',
                resize_strategy='some_resize_strategy',
                deathflag=False,
                unknown_param='some_unknown_param',
            ),
            {
                'hide_strategy': 'some_hide_strategy',
                'resize_strategy': 'some_resize_strategy',
                'deathflag': False,
            },
            {},
        ),
        (helpers.build_exp_value(is_frauder=False), {}, {'is_frauder': False}),
        (helpers.build_exp_value(is_frauder=True), {}, {'is_frauder': True}),
    ],
)
async def test_additional_exp_fields(
        taxi_superapp_misc,
        exp_value,
        expected_additional_modes_params,
        expected_additional_params,
        add_experiment,
):
    add_experiment(consts.SUPERAPP_AVAILABILITY_EXP, exp_value)

    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(),
    )
    assert response.status_code == 200

    expected_json = helpers.ok_response()
    expected_json.update(expected_additional_params)
    eats_mode = [
        mode for mode in expected_json['modes'] if mode['mode'] == 'eats'
    ][0]
    grocery_mode = [
        mode for mode in expected_json['modes'] if mode['mode'] == 'grocery'
    ][0]
    eats_mode['parameters'].update(expected_additional_modes_params)
    grocery_mode['parameters'].update(expected_additional_modes_params)
    assert response.json() == expected_json


@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'deathflag_set, available', [(True, False), (False, True)],
)
async def test_deathflag_affects_availability(
        taxi_superapp_misc, deathflag_set, available, add_experiment,
):
    add_experiment(
        consts.SUPERAPP_AVAILABILITY_EXP,
        helpers.build_exp_value(deathflag=deathflag_set),
    )

    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(),
    )
    assert response.status_code == 200

    eats_mode = helpers.build_mode(
        'eats', available=available, deathflag=deathflag_set,
    )
    grocery_mode = helpers.build_mode(
        'grocery', available=available, deathflag=deathflag_set,
    )

    assert eats_mode in response.json()['modes']
    assert grocery_mode in response.json()['modes']


@pytest.mark.parametrize(
    'payload, should_match',
    [
        (helpers.build_payload(), False),
        (helpers.build_payload(shortcuts={}), False),
        (
            helpers.build_payload(
                shortcuts={'multicolor_service_icons_supported': False},
            ),
            False,
        ),
        (
            helpers.build_payload(
                shortcuts={'multicolor_service_icons_supported': True},
            ),
            True,
        ),
    ],
)
async def test_multicolor_icon_tags_kwargs(
        taxi_superapp_misc, payload, should_match, add_experiment,
):
    # todo: generic "check kwarg is passed" test
    exp_name = 'name'
    exp_value = {'some_exp_value': True}
    add_experiment(
        name=exp_name,
        value=exp_value,
        consumers=['client-superapp-misc/availability'],
        predicate={
            'init': {'arg_name': 'multicolor_service_icons_supported'},
            'type': 'bool',
        },
    )

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    exp_items = response.json()['typed_experiments']['items']
    if not should_match:
        assert not exp_items
        return
    assert len(exp_items) == 1
    result_exp = exp_items[0]
    assert result_exp['name'] == exp_name
    assert result_exp['value'] == exp_value


def make_metric(service):
    return metrics_helpers.Metric(
        labels={
            'sensor': 'availability_product_metrics',
            'source': 'superapp-availability',
            'screen_type': 'main',
            'is_available': '1',
            'superapp_service': service,
        },
        value=1,
    )


@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.config(SUPERAPP_MISC_METRICS_ENABLED=True)
@pytest.mark.parametrize(
    'empty_services, expected_services',
    [
        pytest.param(True, ['taxi'], id='Empty service, only taxi'),
        pytest.param(
            False,
            sorted(['taxi', 'eats', 'grocery']),
            id='Non empty service, taxi, eats, grocery',
        ),
    ],
)
async def test_availability_metrics(
        taxi_superapp_misc,
        taxi_superapp_misc_monitor,
        get_metrics_by_label_values,
        empty_services,
        expected_services,
):
    async with metrics_helpers.MetricsCollector(
            taxi_superapp_misc_monitor,
            sensor='availability_product_metrics',
            labels={
                'source': 'superapp-availability',
                'screen_type': 'main',
                'is_available': '1',
            },
    ) as collector:
        response = await taxi_superapp_misc.post(
            consts.URL, helpers.build_payload(empty_services=empty_services),
        )

    assert response.status == 200

    # todo поправить с https://st.yandex-team.ru/TAXIBACKEND-33479
    metrics = sorted(
        collector.collected_metrics,
        key=lambda m: m.labels['superapp_service'],
    )
    assert metrics == [make_metric(service) for service in expected_services]


@pytest.mark.experiments3(filename='exp3_exp_with_kwarg_point_b.json')
async def test_availability_zeroed_point_b(taxi_superapp_misc):
    payload = helpers.build_payload(
        position=consts.DEFAULT_POSITION,
        eats_available=True,
        grocery_available=True,
        state=helpers.build_state(field_point_b=consts.ZEROED_POSITION),
    )
    response = await taxi_superapp_misc.post(consts.URL, payload)

    assert response.status == 200
