import pytest

from . import utils

MENU_ITEM_ID = 232323
EATER_ID = 'eater2'


@pytest.mark.parametrize('one_as_bool', [True, False])
async def test_options_success(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        one_as_bool,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    core_resp = utils.CoreItemsResponse('123')

    item_1 = utils.PlaceItem(MENU_ITEM_ID, 100, None)

    # test that min_selected is ignored for missing group (0, del)
    group = utils.PlaceOptionGroup(124, min_selected=1, required=False)
    group.add_option(utils.PlaceOption(1124, 10, None))
    item_1.add_option_group(group)

    # test that min_selected is ok to get one option (0)
    group = utils.PlaceOptionGroup(125, min_selected=2, required=False)
    group.add_option(utils.PlaceOption(1125, 10, None, multiplier=5))
    group.add_option(utils.PlaceOption(2125, 10, None, multiplier=5))
    item_1.add_option_group(group)

    # test group wo modifiers (1)
    group = utils.PlaceOptionGroup(126, required=True)
    group.add_option(utils.PlaceOption(1126, 10, None))
    item_1.add_option_group(group)

    # test group with not all modifiers (2)
    group = utils.PlaceOptionGroup(127, required=True)
    group.add_option(utils.PlaceOption(1127, 10, None))
    group.add_option(utils.PlaceOption(2127, 10, None))
    item_1.add_option_group(group)

    # test that requred is ignored for missing group (3, del)
    group = utils.PlaceOptionGroup(128, min_selected=2, required=True)
    group.add_option(utils.PlaceOption(1128, 10, None))
    item_1.add_option_group(group)

    core_resp.add_item(item_1)

    local_services.core_items_response = core_resp.serialize()

    request_options = item_1.get_options_for_request(one_as_bool)

    # test that min_selected is ignored for missing group
    del request_options[0]

    # test that min_selected is ok to get one option
    del request_options[0]['group_options'][1]
    del request_options[0]['modifiers'][1]

    # test group wo modifiers
    del request_options[1]['modifiers']

    # test group with not all modifiers
    del request_options[2]['modifiers'][1]

    # test that requred is ignored for missing group
    del request_options[3]

    response = await utils.add_item(
        taxi_eats_cart,
        local_services,
        item_1,
        EATER_ID,
        one_as_bool=one_as_bool,
        options=request_options,
    )

    cart_item_id = str(response['id'])
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 1

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()
    assert len(options) == 4
    assert utils.pg_result_to_repr(options) == [
        [cart_item_id, '1125', '10.00', 'None', '5'],
        [cart_item_id, '1126', '10.00', 'None', '1'],
        [cart_item_id, '1127', '10.00', 'None', '2'],
        [cart_item_id, '2127', '10.00', 'None', '1'],
    ]

    assert len(response['cart']['items']) == 1
    response_item = response['cart']['items'][0]

    got_options = {}
    for group in response_item['item_options']:
        options = {}
        for option in group['group_options']:
            options[option['id']] = option['quantity']
        got_options[group['group_id']] = options

    expected_options = {
        125: {1125: 5},
        126: {1126: 1},
        127: {1127: 2, 2127: 1},
    }

    assert got_options == expected_options
