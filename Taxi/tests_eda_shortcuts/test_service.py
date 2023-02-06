import pytest

# pylint: disable=import-only-modules
from .conftest import exp3_decorator
from .conftest import get_eda_params

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from eda_shortcuts_plugins.generated_tests import *  # noqa


EXP3_EATS_PARAMS = exp3_decorator(
    name='eda-shortcuts-eats-params', value={'max_shortcuts_count': 10},
)

EXP3_GROCERY_PARAMS = exp3_decorator(
    name='eda-shortcuts-grocery-params', value={'max_shortcuts_count': 10},
)

DEFAULT_HEADERS = {
    'X-Yandex-UID': '12345',
    'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
}


@EXP3_EATS_PARAMS
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.parametrize(
    'eats_enabled, grocery_enabled',
    [(True, True), (True, False), (False, True), (False, False), (None, None)],
)
async def test_services_availability(
        taxi_eda_shortcuts,
        load_json,
        mockserver,
        eats_enabled,
        grocery_enabled,
):
    _mock_eda_catalog_calls = 0

    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        nonlocal _mock_eda_catalog_calls
        _mock_eda_catalog_calls += 1
        return load_json('eda_catalog_shortlist_response.json')

    payload = load_json('dummy.json')
    if eats_enabled is not None and grocery_enabled is not None:
        payload['services_availability'] = [
            {
                'mode': 'eats',
                'parameters': {
                    'available': eats_enabled,
                    'product_tag': 'eats',
                },
            },
            {
                'mode': 'grocery',
                'parameters': {
                    'available': grocery_enabled,
                    'product_tag': 'grocery',
                },
            },
        ]
    else:
        payload.pop('services_availability')

    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops', json=payload, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_eda_catalog_calls == (
        1
        if (eats_enabled or eats_enabled is None)
        or (grocery_enabled or grocery_enabled is None)
        else 0
    )

    scenarios = [i['scenario'] for i in response.json()['scenario_tops']]
    if eats_enabled is None and grocery_enabled is None:
        assert 'eats_place' in scenarios and 'grocery_category' in scenarios
    else:
        assert ('eats_place' in scenarios) == eats_enabled
        assert ('grocery_category' in scenarios) == grocery_enabled


@EXP3_EATS_PARAMS
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
async def test_shortlist_fallback_places(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return {}

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
        },
    )

    assert response.status_code == 200


@EXP3_EATS_PARAMS
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
async def test_shortlist_empty_shortlist_places(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return {'payload': {'places': []}}

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
        },
    )

    assert response.status_code == 200
    obj = response.json()
    assert len(obj['scenario_tops']) == 2

    assert obj['scenario_tops'][0]['scenario'] == 'eats_place'
    assert not obj['scenario_tops'][0]['shortcuts']

    assert obj['scenario_tops'][1]['scenario'] == 'grocery_category'
    assert not obj['scenario_tops'][1]['shortcuts']


@EXP3_EATS_PARAMS
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.parametrize('source', ['shortcuts_admin', 'disk'])
async def test_grocery(
        taxi_eda_shortcuts,
        mockserver,
        testpoint,
        load_json,
        shortcuts_admin_global_mock,
        source,
):
    if source == 'disk':

        @mockserver.handler('/shortcuts-admin/v2/admin/shortcuts/grocery/list')
        def _mock_v2(_):
            return mockserver.make_response(status=500)

    @testpoint('shortcuts-source')
    def _shortcuts_source(src):
        pass

    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
        },
    )

    assert response.status_code == 200
    data = response.json()

    await taxi_eda_shortcuts.enable_testpoints()
    assert (await _shortcuts_source.wait_call())['src'] == source

    _grocery_mock = shortcuts_admin_global_mock['grocery_mock']
    assert _grocery_mock.times_called == int(source == 'shortcuts_admin')

    assert len(data['scenario_tops']) == 2
    assert data['scenario_tops'][1]['scenario'] == 'grocery_category'
    grocery_shortcuts = data['scenario_tops'][1]['shortcuts']

    assert len(grocery_shortcuts) == 4
    scenario_params = grocery_shortcuts[0]['scenario_params'][
        'grocery_category_params'
    ]
    assert scenario_params['place_id'] == '76511'
    assert scenario_params['category_id'] == '1748'
    assert scenario_params['delivery_time'] == {'min': 15, 'max': 25}
    assert grocery_shortcuts[0]['content']['title'] == 'Сладкое'


@exp3_decorator(
    name='eda-shortcuts-eats-params', value={'max_shortcuts_count': 1},
)
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
async def test_shortcuts_max_count(taxi_eda_shortcuts, mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '1234',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj_personal = response.json()
    assert obj_personal['scenario_tops'][0]['scenario'] == 'eats_place'
    assert len(obj_personal['scenario_tops'][0]['shortcuts']) == 1


@exp3_decorator(
    name='eda-shortcuts-eats-params', value={'catalog_ranking_enabled': True},
)
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_personal_eda_ml(taxi_eda_shortcuts, mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        assert 'yandex_uid' in request.json
        return load_json('ordershistory_get_orders_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj_default = response.json()
    assert obj_default['scenario_tops'][0]['scenario'] == 'eats_place'
    assert len(obj_default['scenario_tops'][0]['shortcuts']) == 5

    eda_shortcuts = obj_default['scenario_tops'][0]['shortcuts']
    response_place_id = [
        int(get_eda_params(x, 'place_id')) for x in eda_shortcuts
    ]
    assert response_place_id == [3621, 24938, 24968, 10465, 3265]
    assert get_eda_params(eda_shortcuts[0], 'delivery_time')['min'] == 30
    assert get_eda_params(eda_shortcuts[1], 'delivery_time')['min'] == 35

    assert eda_shortcuts[0].get('tags') is None
    assert eda_shortcuts[1].get('tags') == ['personal']


@exp3_decorator(
    name='eda-shortcuts-eats-params',
    value={
        'hidden_nonpersonal_brand_list': [11787, 1693],
        'hidden_brand_list': [],
    },
)
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_personal_eda_ml_hidden_brands(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        return load_json('ordershistory_get_orders_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
        },
    )

    assert response.status_code == 200

    obj_default = response.json()
    assert obj_default['scenario_tops'][0]['scenario'] == 'eats_place'
    assert len(obj_default['scenario_tops'][0]['shortcuts']) == 4

    eda_shortcuts = obj_default['scenario_tops'][0]['shortcuts']
    response_place_id = [
        int(get_eda_params(x, 'place_id')) for x in eda_shortcuts
    ]
    assert response_place_id == [3621, 24938, 10465, 3265]
    assert get_eda_params(eda_shortcuts[0], 'delivery_time')['min'] == 30
    assert get_eda_params(eda_shortcuts[1], 'delivery_time')['min'] == 35


@EXP3_EATS_PARAMS
@exp3_decorator(
    name='eda-shortcuts-grocery-params',
    value={
        'max_shortcuts_count': 10,
        'personal_categories': [
            {
                'category_id': 'personalcat',
                'image_tag': 'personaltag',
                'title': 'personal',
                'subtitle': 'subpersonal',
                'color': '#F5F4F2',
            },
        ],
        'nonpersonal_categories': [
            {
                'category_id': 'nonpersonalcat',
                'image_tag': 'nonpersonaltag',
                'title': 'personal',
                'subtitle': 'subpersonal',
                'color': '#F5F4F2',
            },
        ],
    },
)
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_grocery_custom_categories(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        if 'yandex_uid' in request.json:
            return load_json('ordershistory_get_orders_response.json')
        return {}

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200
    obj = response.json()
    assert len(obj['scenario_tops']) == 2

    assert obj['scenario_tops'][1]['scenario'] == 'grocery_category'
    assert obj['scenario_tops'][1]['shortcuts']
    assert len(obj['scenario_tops'][1]['shortcuts']) == 6

    grocery_shortcust = obj['scenario_tops'][1]['shortcuts']
    assert (
        grocery_shortcust[0]['scenario_params']['grocery_category_params'][
            'category_id'
        ]
        == 'personalcat'
    )
    assert grocery_shortcust[0].get('tags') == ['personal']
    assert (
        grocery_shortcust[1]['scenario_params']['grocery_category_params'][
            'category_id'
        ]
        == 'nonpersonalcat'
    )
    assert grocery_shortcust[1].get('tags') is None
    assert (
        grocery_shortcust[2]['scenario_params']['grocery_category_params'][
            'category_id'
        ]
        == '1748'
    )
    assert grocery_shortcust[2].get('tags') is None

    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12'},
    )

    assert response.status_code == 200
    obj = response.json()
    assert len(obj['scenario_tops']) == 2

    assert obj['scenario_tops'][1]['scenario'] == 'grocery_category'
    assert obj['scenario_tops'][1]['shortcuts']
    assert len(obj['scenario_tops'][1]['shortcuts']) == 5

    grocery_shortcust = obj['scenario_tops'][1]['shortcuts']
    assert (
        grocery_shortcust[0]['scenario_params']['grocery_category_params'][
            'category_id'
        ]
        == 'nonpersonalcat'
    )


@exp3_decorator(name='eda-shortcuts-eats-params', value={'image_tag_index': 1})
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_image_tag_index_eda_ml(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        assert 'yandex_uid' in request.json
        return load_json('ordershistory_get_orders_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj_default = response.json()
    assert obj_default['scenario_tops'][0]['scenario'] == 'eats_place'
    assert len(obj_default['scenario_tops'][0]['shortcuts']) == 5

    eda_shortcuts = obj_default['scenario_tops'][0]['shortcuts']
    assert eda_shortcuts[0]['content']['image_tag'] == 'imagetag2'


@exp3_decorator(
    name='eda-shortcuts-eats-params',
    value={
        'catalog_ranking_enabled': True,
        'image_tag_index': 1,
        'random_image_tag_enabled': True,
    },
)
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_image_tag_random_eda_ml(
        taxi_eda_shortcuts, mockserver, load_json,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        assert 'yandex_uid' in request.json
        return load_json('ordershistory_get_orders_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj_default = response.json()
    assert obj_default['scenario_tops'][0]['scenario'] == 'eats_place'
    assert len(obj_default['scenario_tops'][0]['shortcuts']) == 5

    eda_shortcuts = obj_default['scenario_tops'][0]['shortcuts']
    assert (
        len(
            list(
                set(eda_shortcut['content']['image_tag'])
                for eda_shortcut in eda_shortcuts
            ),
        )
        > 1
    )


@exp3_decorator(
    name='eda-shortcuts-eats-params', value={'only_personal': True},
)
@EXP3_GROCERY_PARAMS
@pytest.mark.config(EDA_SHORTCUTS_SHORTLIST_ENABLED=True)
@pytest.mark.config(EDA_SHORTCUTS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_only_personal_eda_ml(taxi_eda_shortcuts, mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_catalog(request):
        return load_json('eda_catalog_shortlist_response.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_orders_history(request):
        assert 'yandex_uid' in request.json
        return load_json('ordershistory_get_orders_response.json')

    req_body = load_json('dummy.json')
    response = await taxi_eda_shortcuts.post(
        'eda-shortcuts/v1/tops',
        json=req_body,
        headers={
            'X-Yandex-UID': '12345',
            'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    obj_default = response.json()
    assert obj_default['scenario_tops'][0]['scenario'] == 'eats_place'
    eda_shortcuts = obj_default['scenario_tops'][0]['shortcuts']
    for eda_shortcut in eda_shortcuts:
        assert eda_shortcut.get('tags') == ['personal']
