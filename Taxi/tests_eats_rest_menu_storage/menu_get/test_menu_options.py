import decimal
import typing

import pytest

from tests_eats_rest_menu_storage import models
import tests_eats_rest_menu_storage.menu_get.menu_response as menu_response
import tests_eats_rest_menu_storage.menu_get.utils as utils

BRAND_ID = 1
PLACE_ID = 1


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_items',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_get_items',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_menu_inner_options(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, handler,
):
    _, brand_item_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=1,
    )
    inner_option_uuids = eats_rest_menu_storage.insert_brand_inner_options(
        [
            models.BrandMenuItemInnerOption(  # все данные у бренда
                brand_id=BRAND_ID,
                origin_id='origin_id_1',
                name='brand_inner_option_name_1',
                group_name='brand_group_name_1',
                group_origin_id='group_origin_id_1',
                min_amount=1,
                max_amount=10,
            ),
            models.BrandMenuItemInnerOption(  # все данные у плейса
                brand_id=BRAND_ID,
                origin_id='origin_id_2',
                name='brand_inner_option_name_2',
                group_name='brand_group_name_1',
                group_origin_id='group_origin_id_1',
            ),
            models.BrandMenuItemInnerOption(  # в другой групе
                brand_id=BRAND_ID,
                origin_id='origin_id_3',
                group_origin_id='group_origin_id_2',
                name='brand_inner_option_name_2',
                group_name='brand_group_name_2',
            ),
            models.BrandMenuItemInnerOption(  # удален -  в выдаче его не будет
                brand_id=BRAND_ID,
                origin_id='origin_id_4',
                name='brand_inner_option_name_2',
                group_name='brand_group_name_1',
                group_origin_id='group_origin_id_1',
            ),
        ],
    )
    eats_rest_menu_storage.insert_item_inner_options(
        [
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'origin_id_1')
                ],
                place_menu_item_id=1,
                origin_id='origin_id_1',
            ),
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'origin_id_2')
                ],
                place_menu_item_id=1,
                origin_id='origin_id_2',
                name='brand_inner_option_name_2',
                group_name='brand_group_name_1',
                group_origin_id='group_origin_id_1',
                legacy_id=2,
                min_amount=2,
                max_amount=20,
            ),
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'origin_id_3')
                ],
                place_menu_item_id=1,
                origin_id='origin_id_3',
                group_origin_id='group_origin_id_2',
            ),
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'origin_id_4')
                ],
                place_menu_item_id=1,
                origin_id='origin_id_4',
                group_origin_id='group_origin_id_1',
                deleted=True,
            ),
        ],
    )

    expected_inner_options = [
        menu_response.InnerOption(
            id=inner_option_uuids[(BRAND_ID, 'origin_id_1')],
            origin_id='origin_id_1',
            name='brand_inner_option_name_1',
            group_name='brand_group_name_1',
            group_origin_id='group_origin_id_1',
            min_amount=1,
            max_amount=10,
        ).as_dict(),
        menu_response.InnerOption(
            id=inner_option_uuids[(BRAND_ID, 'origin_id_2')],
            origin_id='origin_id_2',
            name='brand_inner_option_name_2',
            group_name='brand_group_name_1',
            group_origin_id='group_origin_id_1',
            legacy_id=2,
            min_amount=2,
            max_amount=20,
        ).as_dict(),
        menu_response.InnerOption(
            id=inner_option_uuids[(BRAND_ID, 'origin_id_3')],
            origin_id='origin_id_3',
            group_origin_id='group_origin_id_2',
            name='brand_inner_option_name_2',
            group_name='brand_group_name_2',
        ).as_dict(),
    ]

    request = utils.get_basic_request(handler, list(brand_item_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_inner_options = response.json()['places'][0]['items'][0][
            'inner_options'
        ]
    else:
        response_inner_options = response.json()['items'][0]['inner_options']

    assert sorted(
        expected_inner_options, key=lambda d: d['origin_id'],
    ) == sorted(response_inner_options, key=lambda d: d['origin_id'])


def insert_option_groups(eats_rest_menu_storage):
    groups_uuids = eats_rest_menu_storage.insert_brand_option_groups(
        [
            models.BrandMenuItemOptionGroup(  # вся информация у бренда
                brand_id=1,
                origin_id='origin_group_id_1',
                name='brand_group_name_1',
                min_selected_options=1,
                max_selected_options=10,
            ),
            models.BrandMenuItemOptionGroup(  # вся информация у плейса
                brand_id=1,
                origin_id='origin_group_id_2',
                name='brand_group_name_2',
            ),
            models.BrandMenuItemOptionGroup(  # удалён
                brand_id=1,
                origin_id='origin_group_id_3',
                name='brand_group_name_3',
            ),
            models.BrandMenuItemOptionGroup(  # у второго айтема
                brand_id=1,
                origin_id='origin_group_id_4',
                name='brand_group_name_4',
            ),
        ],
    )
    eats_rest_menu_storage.insert_item_option_groups(
        [
            models.PlaceMenuItemOptionGroup(  # вся информация у бренда
                brand_menu_item_option_group=groups_uuids[
                    (1, 'origin_group_id_1')
                ],
                place_menu_item_id=1,
                origin_id='origin_group_id_1',
            ),
            models.PlaceMenuItemOptionGroup(  # вся информация у плейса
                brand_menu_item_option_group=groups_uuids[
                    (1, 'origin_group_id_2')
                ],
                place_menu_item_id=1,
                origin_id='origin_group_id_2',
                legacy_id=2,
                name='place_group_name_2',
                sort=20,
                min_selected_options=2,
                max_selected_options=20,
            ),
            models.PlaceMenuItemOptionGroup(  # удалён
                brand_menu_item_option_group=groups_uuids[
                    (1, 'origin_group_id_3')
                ],
                place_menu_item_id=1,
                origin_id='origin_group_id_3',
                deleted=True,
            ),
        ],
    )

    return groups_uuids


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_option_groups',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_get_option_groups',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_menu_options_groups(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, handler,
):
    _, brand_item_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=1,
    )
    groups_uuids = insert_option_groups(eats_rest_menu_storage)

    expected_options_groups = [
        menu_response.OptionsGroup(  # вся информация у бренда
            id=groups_uuids[(1, 'origin_group_id_1')],
            origin_id='origin_group_id_1',
            name='brand_group_name_1',
            min_selected_options=1,
            max_selected_options=10,
        ).as_dict(),
        menu_response.OptionsGroup(  # вся информация у плейса
            id=groups_uuids[(1, 'origin_group_id_2')],
            origin_id='origin_group_id_2',
            legacy_id=2,
            name='place_group_name_2',
            sort=20,
            min_selected_options=2,
            max_selected_options=20,
        ).as_dict(),
    ]

    request = utils.get_basic_request(handler, list(brand_item_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200

    if handler is utils.HandlerTypes.GET_ITEMS:
        response_options_groups = response.json()['places'][0]['items'][0][
            'options_groups'
        ]
    else:
        response_options_groups = response.json()['items'][0]['options_groups']

    assert sorted(
        expected_options_groups, key=lambda d: d['origin_id'],
    ) == sorted(response_options_groups, key=lambda d: d['origin_id'])


def insert_options(
        eats_rest_menu_storage,
) -> typing.Dict[int, typing.List[menu_response.Option]]:

    option_uuids = eats_rest_menu_storage.insert_brand_menu_item_options(
        [
            models.BrandMenuItemOption(
                brand_id=1,
                origin_id='option_origin_id_1',
                name='brand_option_name_1',
                multiplier=10,
                min_amount=1,
                max_amount=10,
                sort=10,
            ),
            models.BrandMenuItemOption(
                brand_id=BRAND_ID,
                origin_id='option_origin_id_2',
                name='brand_option_name_2',
            ),
            models.BrandMenuItemOption(
                brand_id=BRAND_ID,
                origin_id='option_origin_id_3',
                name='brand_option_name_3',
            ),
            models.BrandMenuItemOption(
                brand_id=BRAND_ID,
                origin_id='option_origin_id_4',
                name='brand_option_name_4',
            ),
        ],
    )
    option_ids = eats_rest_menu_storage.insert_place_menu_item_options(
        [
            models.PlaceMenuItemOption(  # вся информация у бренда
                brand_menu_item_option=option_uuids[(1, 'option_origin_id_1')],
                place_menu_item_option_group_id=1,
                origin_id='option_origin_id_1',
            ),
            models.PlaceMenuItemOption(  # вся информация у плейса
                brand_menu_item_option=option_uuids[(1, 'option_origin_id_2')],
                place_menu_item_option_group_id=1,
                origin_id='option_origin_id_2',
                name='place_option_name_2',
                legacy_id=2,
                multiplier=20,
                min_amount=2,
                max_amount=20,
                sort=20,
            ),
            models.PlaceMenuItemOption(  # у второй группы
                brand_menu_item_option=option_uuids[(1, 'option_origin_id_3')],
                place_menu_item_option_group_id=2,
                origin_id='option_origin_id_3',
            ),
            models.PlaceMenuItemOption(  # удалён
                brand_menu_item_option=option_uuids[(1, 'option_origin_id_4')],
                place_menu_item_option_group_id=2,
                origin_id='option_origin_id_4',
                deleted=True,
            ),
        ],
    )
    eats_rest_menu_storage.insert_item_option_prices(
        [
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=option_ids[
                    (1, 'option_origin_id_1')
                ],
                price=decimal.Decimal(10.5),
            ),
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=option_ids[
                    (1, 'option_origin_id_2')
                ],
                price=decimal.Decimal(10.5),
                promo_price=decimal.Decimal(5.5),
                vat=decimal.Decimal(3.5),
            ),
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=option_ids[
                    (2, 'option_origin_id_3')
                ],
                price=decimal.Decimal(10.5),
            ),
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=option_ids[
                    (2, 'option_origin_id_4')
                ],
                price=decimal.Decimal(10.5),
                deleted=True,
            ),
        ],
    )

    return option_uuids


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS,
            id='test_get_items_options',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
        pytest.param(
            utils.HandlerTypes.MENU,
            id='test_menu_options',
            marks=pytest.mark.pgsql(
                'eats_rest_menu_storage', files=['fill_data.sql'],
            ),
        ),
    ],
)
async def test_menu_options(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, handler,
):
    _, brand_item_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=1,
    )

    insert_option_groups(eats_rest_menu_storage)
    option_uuids = insert_options(eats_rest_menu_storage)

    expected_options = [
        menu_response.Option(
            id=option_uuids[(BRAND_ID, 'option_origin_id_1')],
            origin_id='option_origin_id_1',
            name='brand_option_name_1',
            multiplier=10,
            min_amount=1,
            max_amount=10,
            sort=10,
            price='10.5',
        ).as_dict(),
        menu_response.Option(
            id=option_uuids[(BRAND_ID, 'option_origin_id_2')],
            origin_id='option_origin_id_2',
            name='place_option_name_2',
            legacy_id=2,
            multiplier=20,
            min_amount=2,
            max_amount=20,
            sort=20,
            price='10.5',
            promo_price='5.5',
            vat='3.5',
        ).as_dict(),
        menu_response.Option(
            id=option_uuids[(BRAND_ID, 'option_origin_id_3')],
            origin_id='option_origin_id_3',
            name='brand_option_name_3',
            price='10.5',
        ).as_dict(),
    ]

    request = utils.get_basic_request(handler, list(brand_item_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200

    response_options = []

    if handler is utils.HandlerTypes.GET_ITEMS:
        for option_group in response.json()['places'][0]['items'][0][
                'options_groups'
        ]:
            for option in option_group['options']:
                response_options.append(option)
    else:
        for option_group in response.json()['items'][0]['options_groups']:
            for option in option_group['options']:
                response_options.append(option)

    assert sorted(expected_options, key=lambda d: d['origin_id']) == sorted(
        response_options, key=lambda d: d['origin_id'],
    )


def insert_option_with_statuses(eats_rest_menu_storage, db):
    db.add_option(
        models.PlaceMenuItemOption(  # доступно по статусу
            brand_menu_item_option='',
            place_menu_item_option_group_id=1,
            origin_id='option_origin_id_1',
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(  # недоступно по статусу
            brand_menu_item_option='',
            place_menu_item_option_group_id=1,
            origin_id='option_origin_id_2',
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(  # доступно потому что статуса нет
            brand_menu_item_option='',
            place_menu_item_option_group_id=1,
            origin_id='option_origin_id_3',
        ),
    )

    eats_rest_menu_storage.insert_item_option_statuses(
        [
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=1, active=True,
            ),
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=2, active=False,
            ),
        ],
    )


@pytest.mark.parametrize(
    'handler',
    [
        pytest.param(
            utils.HandlerTypes.GET_ITEMS, id='test_get_items_option_statuses',
        ),
        pytest.param(
            utils.HandlerTypes.MENU, id='test_menu_get_option_statuses',
        ),
    ],
)
async def test_menu_option_statuses(
        taxi_eats_rest_menu_storage,
        eats_rest_menu_storage,
        place_menu_db,
        handler,
):
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    _, brand_item_uuids = utils.default_items_insert(
        eats_rest_menu_storage, item_amount=1,
    )
    insert_option_groups(eats_rest_menu_storage)
    insert_option_with_statuses(eats_rest_menu_storage, db)

    request = utils.get_basic_request(handler, list(brand_item_uuids.values()))

    response = await taxi_eats_rest_menu_storage.post(
        handler.value, json=request,
    )

    assert response.status_code == 200

    expected_options_statuses = {
        'option_origin_id_1': True,
        'option_origin_id_2': False,
        'option_origin_id_3': True,
    }

    response_options_statuses = {}

    if handler is utils.HandlerTypes.GET_ITEMS:
        option_groups = response.json()['places'][0]['items'][0][
            'options_groups'
        ]
        option_groups.sort(key=lambda d: d['origin_id'])
        for option in option_groups[0]['options']:
            response_options_statuses[option['origin_id']] = option[
                'available'
            ]
    else:
        option_groups = response.json()['items'][0]['options_groups']
        option_groups.sort(key=lambda d: d['origin_id'])
        for option in option_groups[0]['options']:
            response_options_statuses[option['origin_id']] = option[
                'available'
            ]

    assert expected_options_statuses == response_options_statuses
