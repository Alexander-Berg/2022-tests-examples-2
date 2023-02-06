import copy

import pytest

from . import utils

PLACE1_BRAND1 = 'place123'
PLACE2_BRAND1 = 'place2'
PLACE3_BRAND2 = 'place3'

PLACE4_BRAND1 = 'place4'


REQUEST_PARAMS = {
    'latitude': 55.75,  # Moscow
    'longitude': 37.62,
    'shippingType': 'delivery',
    'placeSlug': PLACE1_BRAND1,
}


def make_button(id_, action, text_tanker):
    return {
        'title': {
            'color': [
                {'theme': 'light', 'value': '#000000'},
                {'theme': 'dark', 'value': '#ffffff'},
            ],
            'text': text_tanker,
        },
        'id': id_,
        'action': action,
    }


def setup_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_cart_update_cart_place',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        is_config=False,
        clauses=[
            {
                'predicate': {'type': 'true'},
                'enabled': enabled,
                'value': {
                    'reset_cart_dialog': {
                        'description': (
                            'change_dialog.reset_cart_dialog.description'
                        ),
                        'buttons': [
                            make_button(
                                'cancel_button',
                                'cancel',
                                'change_dialog.cancel_button_text',
                            ),
                            make_button(
                                'ok_button',
                                'add_item',
                                'change_dialog.add_item_button_text',
                            ),
                        ],
                    },
                    'can_switch_dialog': {
                        'description': (
                            'change_dialog.can_switch_dialog.description'
                        ),
                        'buttons': [
                            make_button(
                                'cancel_button',
                                'cancel',
                                'change_dialog.cancel_button_text',
                            ),
                            make_button(
                                'delete_button',
                                'add_item',
                                'change_dialog.add_item_button_text',
                            ),
                            make_button(
                                'ok_button',
                                'move_cart',
                                'change_dialog.move_cart_button_text',
                            ),
                        ],
                    },
                },
            },
        ],
    )


@pytest.mark.parametrize(
    [
        'current_place_slug',
        'request_place_slug',
        'expected_change_dialog_filename',
    ],
    [
        pytest.param(
            PLACE1_BRAND1,
            PLACE2_BRAND1,
            'expected_change_dialog_possible.json',
            id='different place slug',
            marks=[setup_experiment(True)],
        ),
        pytest.param(
            PLACE1_BRAND1,
            PLACE3_BRAND2,
            'expected_change_dialog_reset_cart.json',
            id='different place slug, different brands',
            marks=[setup_experiment(True)],
        ),
        pytest.param(
            PLACE1_BRAND1,
            PLACE2_BRAND1,
            None,
            id='different place slug, but experiment is off',
            marks=[setup_experiment(False)],
        ),
        pytest.param(
            PLACE1_BRAND1,
            PLACE4_BRAND1,
            'expected_change_dialog_reset_cart.json',
            id='no requested place in cache',
            marks=[setup_experiment(True)],
        ),
        pytest.param(
            PLACE1_BRAND1,
            PLACE1_BRAND1,
            None,
            id='same place slug - should return no change dialog',
            marks=[setup_experiment(True)],
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.additional_payment_text()
async def test_cart_get_change_dialog(
        taxi_eats_cart,
        local_services,
        load_json,
        current_place_slug,
        request_place_slug,
        expected_change_dialog_filename,
):
    """При запросе другого плейса и выполнении всех условий возможности
    изменения корзины - диалог приходит"""
    local_services.set_place_slug(current_place_slug)
    local_services.core_items_request = ['2', '232323']
    local_services.asap = True
    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )
    local_services.eats_products_items_request = ['2', '232323']
    params = copy.deepcopy(REQUEST_PARAMS)
    params['placeSlug'] = request_place_slug
    local_services.set_params(params)

    response = await taxi_eats_cart.get(
        'api/v1/cart', params=params, headers=utils.get_auth_headers('eater3'),
    )

    assert response.status_code == 200
    resp_json = response.json()
    if expected_change_dialog_filename:
        expected_change_dialog = load_json(expected_change_dialog_filename)
        assert resp_json['change_dialog'] == expected_change_dialog
    else:
        assert 'change_dialog' not in resp_json
