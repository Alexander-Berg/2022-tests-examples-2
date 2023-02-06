import pytest


@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['express', 'cargo', 'courier'],
    },
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_content_happy_path(
        taxi_cargo_toolbar, default_pa_headers, load_json,
):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200
    assert response.json() == load_json(filename='dashboard.json')


@pytest.mark.tariff_settings(filename='tariff_settings_only_express.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_content_only_express(
        taxi_cargo_toolbar, default_pa_headers, load_json,
):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200

    expected = load_json(filename='tariffs_section_express_only.json')
    assert response.json()['sections'][1] == expected


@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['express', 'cargo', 'courier'],
    },
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_content_not_authorized(
        taxi_cargo_toolbar, default_pa_headers, load_json,
):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(filename='dashboard.json')


@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_empty_response(
        taxi_cargo_toolbar, default_pa_headers,
):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
    )
    assert response.status_code == 500


@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_out_of_zone(taxi_cargo_toolbar, default_pa_headers, load_json):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 47.47474747474,
                'latitude': 47.47474747474,
            },
            'accuracy': 0.89343434,
        },
    )
    assert response.status_code == 200

    dashboard = load_json(filename='dashboard.json')
    expected = dict()
    expected['sections'] = [dashboard['sections'][0], dashboard['sections'][3]]
    expected['meta'] = {'sections': ['order-carousel', 'stories']}
    expected['metrica_label'] = 'dashboard-label'

    assert response.json() == expected


@pytest.mark.experiments3(
    name='moscow_cargo_hide',
    consumers=['tariff_visibility_helper'],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['express', 'cargo', 'courier'],
    },
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_category_hidden_by_visibility_config(
        taxi_cargo_toolbar, default_pa_headers, load_json,
):
    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200

    expected = load_json(filename='dashboard.json')
    # deleting cargo tariff info
    del expected['sections'][1]['meta']['tariffs'][2]
    del expected['sections'][1]['widgets'][1]['meta']['tariffs'][2]
    del expected['sections'][1]['widgets'][1]['tiles'][2]
    expected['sections'][1]['widgets'][1]['tiles'][0]['width'] = 3
    expected['sections'][1]['widgets'][1]['tiles'][1]['width'] = 3
    assert response.json() == expected


@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['express', 'cargo', 'courier'],
    },
    CARGO_TOOLBAR_APPLY_SURGE_IN_DASHBOARD=True,
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dashboard_surge(
        taxi_cargo_toolbar, default_pa_headers, load_json, mockserver,
):
    @mockserver.json_handler('/surge-calculator/v1/calc-surge')
    def v1_calc_surge(request):
        surge = dict(
            experiment_layer='default',
            is_cached=False,
            experiment_id='experiment_id',
            experiment_name='experiment_name',
            calculation_id='so_awfully_huge_surge',
            classes=[
                {
                    'name': 'express',
                    'value_raw': 1.0,
                    'surge': {'value': 1.575},
                },
                {
                    'name': 'cargo',
                    'value_raw': 1.0,
                    'surge': {'value': 0.0003},
                },
                {'name': 'courier', 'value_raw': 1.0, 'surge': {'value': 1.0}},
            ],
            experiments=[],
            experiment_errors=[],
        )
        return mockserver.make_response(json=surge, status=200)

    response = await taxi_cargo_toolbar.post(
        '/4.0/cargo-c2c/v1/dashboard/content',
        json={
            'coordinate': {
                'longitude': 37.1946401739712,
                'latitude': 55.478983901730004,
            },
            'accuracy': 0.89343434,
        },
        headers=default_pa_headers('phone_pd_id'),
    )
    assert response.status_code == 200

    response_categories = response.json()['sections'][1]['widgets'][1]['tiles']
    assert response_categories[1]['tile']['header']['subtitle'] == 'от 393 ₽'
    assert response_categories[2]['tile']['header']['subtitle'] == 'от 0.07 ₽'
    assert response_categories[1]['tile']['meta']['minimal_price'] == '393 ₽'
    assert response_categories[2]['tile']['meta']['minimal_price'] == '0.07 ₽'
