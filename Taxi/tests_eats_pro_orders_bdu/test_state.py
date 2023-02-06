import dateutil
import pytest

from tests_eats_pro_orders_bdu import models


def decorate_screen_filename(screen_filename: str, **kwargs):
    result = screen_filename
    for key in sorted(kwargs):
        if kwargs[key]:
            result += '_' + key
    return result + '.json'


@pytest.mark.parametrize(
    'cargo',
    [
        {'is_deaf_performer': True, 'batch': True},
        {'is_deaf_performer': False, 'batch': True},
        {'is_deaf_performer': True, 'batch': False},
        {'is_deaf_performer': False, 'batch': False},
    ],
    indirect=True,
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_screen_to_restaurant(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        load_json,
        cargo,
        mock_driver_tags_v1_match_profile,
):
    assert hasattr(cargo, 'performer_info')
    assert 'is_deaf' in cargo.performer_info

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    result_screen_filename = decorate_screen_filename(
        'screen_to_restaurant',
        batch=cargo.batch,
        with_deaf_performer=cargo.performer_info['is_deaf'],
    )
    screen_to_restaurant = load_json(result_screen_filename)
    print(response.text)
    assert response.json()['state']['ui']['items'] == screen_to_restaurant
    assert response.json()['state']['point']['actions'] == [
        {'title': 'В Ресторане', 'type': 'arrived_at_point'},
        {'coordinates': [37.642979, 55.734977], 'type': 'navigator'},
    ]


@pytest.mark.parametrize(
    'cargo', [{'batch': True}, {'batch': False}], indirect=True,
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@pytest.mark.translations()
@models.TIMER_CONFIG_ETA_TEXT
async def test_screen_in_restaurant(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        load_json,
        cargo,
        mock_driver_tags_v1_match_profile,
):
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    if cargo.batch is True:
        cargo.waybill['execution']['points'][1]['visit_status'] = 'arrived'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    result_screen_filename = decorate_screen_filename(
        'screen_in_restaurant', batch=cargo.batch,
    )
    screen_in_restaurant = load_json(result_screen_filename)
    assert response.json()['state']['ui']['items'] == screen_in_restaurant


@pytest.mark.parametrize(
    'cargo',
    [
        {'is_deaf_performer': True, 'batch': True},
        {'is_deaf_performer': False, 'batch': False},
    ],
    indirect=True,
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@pytest.mark.experiments3(filename='cargo_orders_hide_address.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_screen_to_client(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        load_json,
        cargo,
        mock_driver_tags_v1_match_profile,
):

    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    if cargo.batch is True:
        cargo.waybill['execution']['points'][1]['visit_status'] = 'arrived'
        cargo.waybill['execution']['points'][1]['is_resolved'] = True

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    result_screen_filename = decorate_screen_filename(
        'screen_to_client',
        batch=cargo.batch,
        with_deaf_performer=cargo.performer_info['is_deaf'],
    )
    screen_to_client = load_json(result_screen_filename)
    assert response.json()['state']['ui']['items'] == screen_to_client
    assert response.json()['state']['point']['actions'] == [
        {'title': 'У Клиента', 'type': 'arrived_at_point'},
        {'coordinates': [37.583, 55.8873], 'type': 'navigator'},
    ]


@pytest.mark.parametrize(
    'cargo', [{'batch': True}, {'batch': False}], indirect=True,
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@pytest.mark.experiments3(filename='cargo_orders_hide_address.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_screen_at_client(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        load_json,
        cargo,
        mock_driver_tags_v1_match_profile,
):
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['points'][1]['visit_status'] = 'arrived'
    if cargo.batch is True:
        cargo.waybill['execution']['points'][1]['is_resolved'] = True
        cargo.waybill['execution']['points'][2]['visit_status'] = 'arrived'

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    result_screen_filename = decorate_screen_filename(
        'screen_at_client', batch=cargo.batch,
    )
    screen_at_client = load_json(result_screen_filename)
    assert response.json()['state']['ui']['items'] == screen_at_client


@pytest.mark.parametrize(
    ('showed', 'current_time'),
    [(True, '2020-06-17T22:40:01+0300'), (False, '2020-06-17T22:39:55+0300')],
)
@pytest.mark.experiments3(filename='eats_pro_orders_bdu_order_not_ready.json')
@pytest.mark.translations()
@models.TIMER_CONFIG_ETA_TEXT
async def test_order_not_ready(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo,
        mocked_time,
        showed,
        current_time,
        mock_driver_tags_v1_match_profile,
):
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    mocked_time.set(dateutil.parser.isoparse(current_time))
    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    item = response.json()['state']['ui']['items'][2]['items'][2]
    if showed:
        assert (
            item['type'] == 'custom' and item['subtype'] == 'order_not_ready'
        )
    else:
        assert item['type'] != 'custom'


@pytest.mark.parametrize(
    ('updated', 'current_time'),
    [(True, '2020-06-17T22:40:01+0300'), (False, '2020-06-17T22:39:43+0300')],
)
@pytest.mark.experiments3(
    filename='eats_pro_orders_bdu_orders_preparation_late.json',
)
@pytest.mark.translations()
@models.TIMER_CONFIG_ETA_TEXT
async def test_order_late(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo,
        mocked_time,
        updated,
        current_time,
        mock_driver_tags_v1_match_profile,
):
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    mocked_time.set(dateutil.parser.isoparse(current_time))
    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    item = response.json()['state']['ui']['items'][2]['items'][0]
    if updated:
        assert item['right_tip']['background_color'] == '#F5523A'
    else:
        assert item['right_tip']['background_color'] == 'main_yellow'
