import pytest

CCWPBZ_CONF1 = {
    '__default__': {},
    'moscow': {'*': ['cargo', 'delivery'], 'vip': ['vip', 'comfortplus']},
}

CCWPBZ_CONF2 = {
    '__default__': {},
    'moscow': {
        'vip': ['vip', 'business', 'ultimate', 'comfortplus'],
        'business': ['business', 'vip', 'econom'],
        'comfortplus': ['comfort'],
        'cargo': ['cargo'],
    },
}


@pytest.fixture(autouse=True)
def classifier_request_override(mockserver):
    @mockserver.json_handler('/classifier/v1/classifiers/updates')
    def _mock_classifiers_updates(request):
        return {
            'limit': 100,
            'classifiers': [{'classifier_id': 'Москва', 'is_allowing': True}],
        }

    @mockserver.json_handler('/classifier/v1/classifier-tariffs/updates')
    def _mock_tariffs_updates(request):
        response = {
            'cursor': {'id': 5},
            'limit': 100,
            'tariffs': [
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'vip',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'comfortplus',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': True,
                    'tariff_id': 'cargo',
                },
            ],
        }
        return response

    @mockserver.json_handler('/classifier/v1/classification-rules/updates')
    def _mock_classification_rules_updates(request):
        response = {
            'classification_rules': [
                {
                    'classifier_id': 'Москва',
                    'tariff_id': 'vip',
                    'is_allowing': True,
                    'price_from': 1200000,
                    'year_from': 2013,
                },
                {
                    'classifier_id': 'Москва',
                    'tariff_id': 'comfortplus',
                    'is_allowing': True,
                    'price_from': 40000,
                    'year_from': 2013,
                },
            ],
            'limit': 100,
        }
        return response


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    CLASSES_WITHOUT_PERMIT_BY_ZONES_FILTER_ENABLED=True,
)
@pytest.mark.parametrize(
    'driver_candidates, config, allowed_classes, expected_response',
    [
        pytest.param(
            ['dbid0_uuid0'],
            CCWPBZ_CONF1,
            ['cargo'],
            ['uuid0'],
            id='cargo_no_permit_needed',
        ),
        pytest.param(
            ['dbid0_uuid3'],
            CCWPBZ_CONF1,
            ['vip'],
            ['uuid3'],
            id='vip_permit_by_classifier_self_to_self',
        ),
        pytest.param(
            ['dbid0_uuid3'],
            CCWPBZ_CONF1,
            ['comfortplus'],
            ['uuid3'],
            id='vip_permit_by_classifier_self_to_other',
        ),
        pytest.param(
            ['dbid0_uuid1'],
            CCWPBZ_CONF1,
            ['comfortplus'],
            None,
            id='comfortplus_no_permit_classifier_disalow',
        ),
        pytest.param(
            ['dbid0_uuid0', 'dbid0_uuid3', 'dbid0_uuid2'],
            CCWPBZ_CONF1,
            ['vip', 'comfortplus'],
            ['uuid3'],
            id='multiple_check_one_allow_by_classifier',
        ),
        pytest.param(
            ['dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid3'],
            CCWPBZ_CONF1,
            ['cargo', 'vip', 'comfortplus'],
            ['uuid0', 'uuid3'],
            id='multiple_check_multiple_allow',
        ),
        pytest.param(
            ['dbid0_uuid0'],
            CCWPBZ_CONF2,
            ['cargo'],
            ['uuid0'],
            id='no_without_permit_allow_by_config',
        ),
        pytest.param(
            ['dbid0_uuid0', 'dbid0_uuid3'],
            CCWPBZ_CONF2,
            ['express'],
            None,
            id='no_without_permit_not_in_config_disallow',
        ),
        pytest.param(
            ['dbid0_uuid3', 'dbid0_uuid2'],
            CCWPBZ_CONF2,
            ['econom'],
            ['uuid2'],
            id='no_without_permit_allow_by_config_self_to_self_1',
        ),
        # comfort in Moscow is not allowed at all
        # pytest.param(
        #    ['dbid0_uuid3', 'dbid0_uuid1'],
        #    CCWPBZ_CONF2,
        #    ['comfort'],
        #    ['uuid1'],
        #    id='no_without_permit_allow_by_config_self_to_self_2',
        # ),
    ],
)
async def test_fetcher_permits_car_no_permits(
        taxi_candidates,
        taxi_config,
        driver_positions,
        driver_candidates,
        config,
        allowed_classes,
        expected_response,
):
    taxi_config.set_values(dict(CLASSES_WITHOUT_PERMIT_BY_ZONES=config))
    await driver_positions(
        [
            {'dbid_uuid': driver, 'position': [55, 35]}
            for driver in driver_candidates
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/class', 'partners/fetch_permits_classes'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': allowed_classes,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    if expected_response:
        assert len(drivers) == len(expected_response)
        assert all([driver['uuid'] in expected_response for driver in drivers])
    else:
        assert not drivers
