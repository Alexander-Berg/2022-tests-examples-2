import pytest

from . import common
from . import const
from . import experiments

DEFAULT_LANG = 'en'


def _prepare_tristero_parcels(tristero_parcels, yandex_uid):
    tristero_parcels.set_yandex_uid(yandex_uid)

    order1 = tristero_parcels.add_order(
        order_id='3b8d1af1-4266-4fde-8246-26a7c19e2bd9',
        ref_order='tristero-order-12345',
        token='order-token-12345',
        vendor='beru',
        status='delivered_partially',
        uid=yandex_uid,
    )
    order1.add_parcel(
        parcel_id='01234567-89ab-cdef-000f-123456789:st-pa',
        status='in_depot',
        description='parcel-1-1-description',
        title='parcel-1-1-title',
        image_url_template='parcel-1-1-image',
    )
    order1.add_parcel(
        parcel_id='01234567-89ab-cdef-000f-987654321:st-pa',
        status='delivered',
        description='parcel-1-2-description',
        title='parcel-1-2-title',
        image_url_template='parcel-1-2-image',
    )

    order2 = tristero_parcels.add_order(
        order_id='b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
        ref_order='tristero-order-abcdefg',
        token='order-token-abcdefg',
        vendor='d-mir',
        status='received',
        uid=yandex_uid,
    )
    order2.add_parcel(
        parcel_id='76543210-89ab-cdef-123f-123456789:st-pa',
        status='in_depot',
        description='parcel-2-1-description',
        title='parcel-2-1-title',
        image_url_template='parcel-2-1-image',
        can_left_at_door=False,
    )


# POST /lavka/v1/api/v1/modes/root
# Перекладывает и локализует ответ tristero-parcels
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_modes_root_mode_parcels_v2(
        taxi_grocery_api, locale, load_json, experiments3, tristero_parcels,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    location = const.LOCATION
    yandex_uid = 'some_uid'

    _prepare_tristero_parcels(tristero_parcels, yandex_uid)

    json = {'modes': ['parcels_v2'], 'position': {'location': location}}
    headers = {}
    if locale:
        headers['Accept-Language'] = locale
    headers['X-Yandex-UID'] = yandex_uid

    expected_response = load_json(
        'modes_mode_parcels_v2_expected_response.json',
    )[locale or DEFAULT_LANG]
    expected_products = [
        product['id'] for product in expected_response['products']
    ]

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )

    assert response.status_code == 200
    assert tristero_parcels.retrieve_orders_times_called == 1

    products = [product['id'] for product in response.json()['products']]
    assert products == expected_products


# POST /lavka/v1/api/v1/modes/root
# Отвечает двести, когда tristero-parcels отвечает 500
# mode parcels_v2 присутствует в ответе, но список items в нём будет пуст
async def test_modes_root_mode_parcels_v2_tristero_error(
        taxi_grocery_api, experiments3, tristero_parcels_500,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)

    location = const.LOCATION

    json = {'modes': ['parcels_v2'], 'position': {'location': location}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json,
    )
    assert response.status_code == 200
    assert tristero_parcels_500.retrieve_orders_times_called == 1
    assert response.json() == {
        'informers': [],
        'modes': [{'items': [], 'mode': 'parcels_v2'}],
        'products': [],
    }


# POST /lavka/v1/api/v1/modes/category-group
# Перекладывает и локализует ответ tristero-parcels
@pytest.mark.parametrize('locale', [None, 'ru', 'en'])
async def test_modes_category_group_mode_parcels_v2(
        taxi_grocery_api, locale, load_json, experiments3, tristero_parcels,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    location = const.LOCATION
    yandex_uid = 'some_uid'

    _prepare_tristero_parcels(tristero_parcels, yandex_uid)

    json = {
        'modes': ['parcels_v2'],
        'position': {'location': location},
        'layout_id': 'not-used-for-parcels',
        'group_id': 'not-used-for-parcels',
    }
    headers = {}
    if locale:
        headers['Accept-Language'] = locale
    headers['X-Yandex-UID'] = yandex_uid

    expected_response = load_json(
        'modes_mode_parcels_v2_expected_response.json',
    )[locale or DEFAULT_LANG]
    expected_products = [
        product['id'] for product in expected_response['products']
    ]

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert tristero_parcels.retrieve_orders_times_called == 1

    products = [product['id'] for product in response.json()['products']]
    assert products == expected_products


# Отвечает двести, когда эксперимент lavka_parcel выключен,
# mode parcels_v2 присутствует в ответе, но список items в нём будет пуст
@pytest.mark.parametrize(
    'handler',
    ['/lavka/v1/api/v1/modes/root', '/lavka/v1/api/v1/modes/category-group'],
)
@pytest.mark.parametrize('experiment_exists', [True, False])
async def test_mode_parcels_v2_no_experiment(
        taxi_grocery_api,
        handler,
        experiment_exists,
        experiments3,
        tristero_parcels_500,
):
    if experiment_exists:
        experiments.lavka_parcel_config(experiments3, enabled=False)
    location = const.LOCATION

    json = {
        'modes': ['parcels_v2'],
        'position': {'location': location},
        'layout_id': 'not-used-for-parcels',
        'group_id': 'not-used-for-parcels',
        'category_id': 'not-used-for-parcels',
    }

    response = await taxi_grocery_api.post(handler, json=json)
    assert response.status_code == 200
    assert tristero_parcels_500.retrieve_orders_times_called == 0
    assert response.json() == {
        'informers': [],
        'modes': [{'items': [], 'mode': 'parcels_v2'}],
        'products': [],
    }


# Отвечает двести, когда эксперимент lavka_parcel выключен,
# mode parcels_v2 присутствует в ответе, но список items в нём будет пуст
@pytest.mark.parametrize('experiment_exists', [True, False])
async def test_modes_category_parcels_v2_no_experiment(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        experiment_exists,
        experiments3,
):
    if experiment_exists:
        experiments.lavka_parcel_config(experiments3, enabled=False)
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    json = {
        'modes': ['parcels_v2'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'informers': [],
        'modes': [{'items': [], 'mode': 'parcels_v2'}],
        'products': [],
    }


# POST /lavka/v1/api/v1/modes/category-group
# Отвечает двести, когда tristero-parcels отвечает 500
# mode parcels_v2 присутствует в ответе, но список items в нём будет пуст
async def test_modes_category_group_mode_parcels_v2_tristero_error(
        taxi_grocery_api, experiments3, tristero_parcels_500,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    location = const.LOCATION

    json = {
        'modes': ['parcels_v2'],
        'position': {'location': location},
        'layout_id': 'not-used-for-parcels',
        'group_id': 'not-used-for-parcels',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category-group', json=json,
    )
    assert response.status_code == 200
    assert tristero_parcels_500.retrieve_orders_times_called == 1
    assert response.json() == {
        'informers': [],
        'modes': [{'items': [], 'mode': 'parcels_v2'}],
        'products': [],
    }


# POST /lavka/v1/api/v1/modes/root
# Проверяем что mode parcels_v2
# присылает название и картинку посылки из tristero-parcels
async def test_modes_root_parcel_title_image(
        taxi_grocery_api, load_json, experiments3, tristero_parcels,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    location = const.LOCATION
    yandex_uid = 'some_uid'

    _prepare_tristero_parcels(tristero_parcels, yandex_uid)

    json = {'modes': ['parcels_v2'], 'position': {'location': location}}
    headers = {}
    headers['Accept-Language'] = 'ru'
    headers['X-Yandex-UID'] = yandex_uid

    expected_response = load_json(
        'modes_mode_parcels_v2_expected_response.json',
    )['ru']

    expected_parcels = []
    for product in expected_response['products']:
        if product['type'] != 'parcels_item':
            continue
        parcel_id_title_img = (
            product['id'],
            product['title'],
            product['image_url_template'],
        )
        expected_parcels.append(parcel_id_title_img)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )

    assert response.status_code == 200
    assert tristero_parcels.retrieve_orders_times_called == 1

    parcels = []
    for product in response.json()['products']:
        if product['type'] != 'parcels_item':
            continue
        parcel_id_title_img = (
            product['id'],
            product['title'],
            product['image_url_template'],
        )
        parcels.append(parcel_id_title_img)

    assert parcels == expected_parcels


# POST /lavka/v1/api/v1/modes/root
# Проверяем что mode parcels_v2
# присылает restrictions и содержит parcel_too_expensive
# если посылку нельзя оставлять у двери
async def test_modes_root_parcel_restrictions(
        taxi_grocery_api, load_json, experiments3, tristero_parcels,
):
    experiments.lavka_parcel_config(experiments3, enabled=True)
    location = const.LOCATION
    yandex_uid = 'some_uid'

    _prepare_tristero_parcels(tristero_parcels, yandex_uid)

    json = {'modes': ['parcels_v2'], 'position': {'location': location}}
    headers = {}
    headers['Accept-Language'] = 'ru'
    headers['X-Yandex-UID'] = yandex_uid

    expected_response = load_json(
        'modes_mode_parcels_v2_expected_response.json',
    )['ru']

    expected_parcels = []
    for product in expected_response['products']:
        if product['type'] != 'parcels_item':
            continue
        parcel_restrictions = (product['id'], product['restrictions'])
        expected_parcels.append(parcel_restrictions)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/root', json=json, headers=headers,
    )

    assert response.status_code == 200
    assert tristero_parcels.retrieve_orders_times_called == 1

    parcels = []
    for product in response.json()['products']:
        if product['type'] != 'parcels_item':
            continue
        parcel_restrictions = (product['id'], product['restrictions'])
        parcels.append(parcel_restrictions)

    assert parcels == expected_parcels
