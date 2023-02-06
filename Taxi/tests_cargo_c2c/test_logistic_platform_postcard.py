import pytest

from testsuite.utils import matching


async def get_sharing_key(
        taxi_cargo_c2c, order_id, order_provider_id, phone_pd_id=None,
):
    response = await taxi_cargo_c2c.post(
        '/v1/clients-orders',
        json={'order_id': order_id, 'order_provider_id': order_provider_id},
    )
    assert response.status_code == 200

    orders = response.json()['orders']
    for order in orders:
        if order['id']['phone_pd_id'] == phone_pd_id:
            return order['sharing_key']

    return orders[0]['sharing_key']


POSTCARD_CONTENT_ITEM = {
    'id': matching.uuid_string,
    'postcard': {
        'cell_title': 'Вам открытка',
        'content': {'type': 'bitmap', 'url': matching.any_string},
        'summary_postcard': 'Уже в пути',
        'user_message': (
            'Will deliver everything you want and everything you need'
        ),
    },
    'subtitle': {
        'color': 'TextMinor',
        'max_lines': 1,
        'text': 'Will deliver everything you want and everything you need',
        'typography': 'caption1',
    },
    'title': {
        'color': 'TextMain',
        'max_lines': 1,
        'text': 'Вам открытка',
        'typography': 'body2',
    },
    'type': 'postcard',
}


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(filename='fake_postcard_enabled_for_lp.json')
@pytest.mark.parametrize(
    'user_language, image_id',
    [('ru', 'image_id_1'), ('en', 'image_id_2'), ('hy', 'image_id_1')],
)
async def test_fake_postcard_in_state(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        mock_admin_images,
        user_language,
        image_id,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', language=user_language),
    )
    assert response.status_code == 200
    assert response.json()['state']['postcard'] == {
        'cell_title': 'Вам открытка',
        'content': {
            'type': 'bitmap',
            'url': f'https://tc.mobile.yandex.net/static/images/{image_id}',
        },
        'summary_postcard': 'Уже в пути',
        'user_message': (
            'Will deliver everything you want and everything you need'
        ),
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(filename='fake_postcard_enabled_for_lp.json')
async def test_fake_postcard_in_content_sections(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        mock_admin_images,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', language='ru'),
    )
    assert response.status_code == 200
    assert (
        POSTCARD_CONTENT_ITEM
        in response.json()['state']['content_sections'][0]['items']
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(filename='fake_postcard_enabled_for_lp.json')
async def test_fake_postcard_in_shared_route(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        mock_admin_images,
):
    await create_logistic_platform_orders()
    key = await get_sharing_key(
        taxi_cargo_c2c,
        get_default_order_id(),
        'logistic-platform',
        'phone_pd_id_2',
    )
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert (
        POSTCARD_CONTENT_ITEM
        in response.json()['content_sections'][0]['items']
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(filename='fake_postcard_enabled_for_lp.json')
async def test_fake_postcard_auto_open(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        mock_admin_images,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_2', language='ru'),
    )
    assert response.status_code == 200
    context = response.json()['deliveries'][0]['state']['context']
    assert context['auto_open_postcard'] is True
