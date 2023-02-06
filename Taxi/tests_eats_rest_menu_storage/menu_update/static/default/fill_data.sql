-- places
insert into eats_rest_menu_storage.brands (id) values (1);
insert into eats_rest_menu_storage.places(
    id, brand_id, slug
) values (1, 1, 'slug1');

-- items
insert into eats_rest_menu_storage.brand_menu_items (
    id, brand_id, origin_id, name, adult,
    description, weight_value, weight_unit, short_name
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'item_origin_id_1',
        'name1', false, 'description1', 10.0, 'ml', null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'item_origin_id_2',
        'name2', true, 'description2', 20.0, 'l', null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'item_origin_id_3',
        'name3', false, 'description3', 30.0, 'g', null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'item_origin_id_4',
        'name4', true, 'description4', 40.0, 'kg', null
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1, 'item_origin_id_5',
        'name5', false, 'description5', 50.0, 'ml', null
    );

insert into eats_rest_menu_storage.place_menu_items (
    brand_menu_item_id, place_id, origin_id, name, adult,
    description, weight_value, weight_unit, sort, shipping_types,
    legacy_id, ordinary, choosable, deleted_at, short_name, updated_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'item_origin_id_1',
        'name1', null, null, null, null, 100, '{delivery,pickup}', 1, true, true, null, null, '2020-01-01T01:01:01.000+03:00'
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'item_origin_id_2',
        'name2', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null, 'short_name_2', '2020-01-01T01:01:01.000+03:00'
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'item_origin_id_3',
        'name3', null, null, 35.0, 'g', 300, '{delivery,pickup}', 3, false, false, '2020-01-01T01:01:01.000+03:00', null, '2020-01-01T01:01:01.000+03:00'
    );

insert into eats_rest_menu_storage.place_menu_item_prices (
    place_menu_item_id, price, promo_price, vat, deleted_at, updated_at
) values
    (1, 10.0, null, null, null, '2020-01-01T00:00:00.000+03:00'),
    (2, 20.0, 19.0, 5.1, null, '2020-01-01T00:00:00.000+03:00'),
    (3, 30.0, 29.0, 3.3, '2020-01-01T00:00:00.000+03:00', '2020-01-01T00:00:00.000+03:00');

--pictures
insert into eats_rest_menu_storage.pictures (
    url, ratio
) values
    ('url1', 1.0),
    ('url2', 0.5),
    ('url3', 1.0),
    ('url30', null);

insert into eats_rest_menu_storage.item_pictures (
    place_menu_item_id, picture_id, deleted_at
) values (1, 1, null), (2, 2, now()), (2, 3, null);

--inner options
insert into eats_rest_menu_storage.brand_menu_item_inner_options (
    id, brand_id, origin_id, name, group_name, group_origin_id,
    min_amount, max_amount
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'inner_option_origin_id_1',
        'inner_option_name1', 'inner_option_group_name1', 'inner_option_group_origin_id_1', 1, 10
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'inner_option_origin_id_2',
        'inner_option_name2', 'inner_option_group_name2', 'inner_option_group_origin_id_2', 3, 5
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'inner_option_origin_id_3',
        'inner_option_name3', 'inner_option_group_name3', 'inner_option_group_origin_id_3', 1, null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'inner_option_origin_id_4',
        'inner_option_name4', 'inner_option_group_name4', 'inner_option_group_origin_id_4', null, 10
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1, 'inner_option_origin_id_5',
        'inner_option_name5', 'inner_option_group_name5', 'inner_option_group_origin_id_5', null, null
    );

insert into eats_rest_menu_storage.place_menu_item_inner_options (
    brand_menu_item_inner_option, place_menu_item_id, origin_id, legacy_id,
    name, group_name, group_origin_id, min_amount, max_amount, deleted_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'inner_option_origin_id_1',
        1, 'other_inner_option_name1', 'other_inner_option_group_name1',
        'other_inner_option_group_origin_id_5', 100, 200, null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 3, 'inner_option_origin_id_2',
        2, null, 'other_inner_option_group_name2', null, null, null, now()
    ),
    (
        '33333333-3333-3333-3333-333333333333', 2, 'inner_option_origin_id_3',
        3, null, null, 'other_inner_option_group_origin_id_3', null, 100, null
    );

--option groups
insert into eats_rest_menu_storage.brand_menu_item_option_groups (
    id, brand_id, origin_id, name, min_selected_options, max_selected_options
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'option_group_origin_id_1',
        'option_group_name1', 5, 10
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'option_group_origin_id_2',
        'option_group_name2', 1, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'option_group_origin_id_3',
        'option_group_name3', null, null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'option_group_origin_id_4',
        'option_group_name4', null, 20
    );


insert into eats_rest_menu_storage.place_menu_item_option_groups (
    brand_menu_item_option_group, place_menu_item_id, origin_id,
    legacy_id, name, sort, min_selected_options, max_selected_options,
    deleted_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'option_group_origin_id_1',
        1, 'other_option_group_name1', 10, 6, 11, null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'option_group_origin_id_2',
        2, null, null, null, null, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 2, 'option_group_origin_id_3',
        3, null, 123, null, 100, null
    ),
    (
        '11111111-1111-1111-1111-111111111111', 3, 'option_group_origin_id_1',
        3, null, 123, null, 100, now()
    );

-- options
insert into eats_rest_menu_storage.brand_menu_item_options (
    id, brand_id, origin_id, name, multiplier, min_amount, max_amount, sort
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'option_origin_id_1',
        'option_name_1', 2, 1, 20, 1
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'option_origin_id_2',
        'option_name_2', 1, null, null, 2
    );

insert into eats_rest_menu_storage.place_menu_item_options (
    brand_menu_item_option, place_menu_item_option_group_id, origin_id,
    legacy_id, name, multiplier, min_amount, max_amount, sort, deleted_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'option_origin_id_1',
        1, 'other_option_name_1', 10, 6, 11, 5, null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 4, 'option_origin_id_2',
        2, null, null, null, null, null, now()
    );

insert into eats_rest_menu_storage.place_menu_item_option_prices (
    place_menu_item_option_id, price, promo_price, vat, deleted_at
) values
    (1, 10.0, null, null, null),
    (2, 20.0, 19.0, 5.1, now());
    
insert into eats_rest_menu_storage.brand_menu_categories (
    id, brand_id, origin_id, name
) values
    (
        '11111111-1111-1111-1111-111111111111', 1,
        'category_origin_id_1', 'category_name_1'
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1,
        'category_origin_id_2', 'category_name_2'
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1,
        'category_origin_id_3', 'category_name_3'
    ),
    (
        '99999999-9999-9999-9999-999999999999', 1,
        'category_origin_id_9', 'category_name_9'
    );

-- categories
insert into eats_rest_menu_storage.place_menu_categories (
    brand_menu_category_id, place_id, origin_id, sort,
    legacy_id, name, schedule, deleted_at, updated_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1,
        'category_origin_id_1', 1, 1, null, null, null, '2020-01-01T01:01:01.000+03:00'
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1,
        'category_origin_id_2', 2, 2, 'other_category_name_2',
        '[
            {
                "day": 1,
                "from": 720,
                "to": 795
            },
            {
                "day": 2,
                "from": 720,
                "to": 795
            }
        ]', null, '2020-01-01T01:01:01.000+03:00'
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1,
        'category_origin_id_3', null, null, null, null, now(), '2020-01-01T01:01:01.000+03:00'
    ),
    ( --неверное расписание
        '99999999-9999-9999-9999-999999999999', 1,
        'category_origin_id_9', null,null,'category_name_9',
        '[
            {
                "day": 1,
                "from": 720,
                "to": 795
            }
        ]', null, '2020-01-01T01:01:01.000+03:00'
    );

insert into eats_rest_menu_storage.category_pictures (
    place_menu_category_id, picture_id, deleted_at
) values (1, 4, null), (2, 4, now());

insert into eats_rest_menu_storage.category_relations (
    place_id, category_id, parent_id, deleted_at
) values (1, 2, 1, null), (1, 3, 2, now());

insert into eats_rest_menu_storage.place_menu_item_categories (
    place_id, place_menu_category_id, place_menu_item_id, deleted_at
) values (1, 1, 1, null), (1, 2, 2, now()), (1, 2, 3, null);

insert into eats_rest_menu_storage.place_menu_item_stocks (
    place_menu_item_id, stock, updated_at
) values
    (1, 10, '2020-01-01T00:00:00.000+03:00'),
    (2, 20, '2020-01-01T00:00:00.000+03:00');

insert into eats_rest_menu_storage.place_menu_item_option_statuses (
    place_menu_item_option_id, active
) values
    (1, true),
    (2, true);

insert into eats_rest_menu_storage.place_menu_item_statuses (
    place_menu_item_id, active, updated_at
) values
    (1, true, '2020-01-01T01:01:01.000+03:00'),
    (2, true, '2020-01-01T01:01:01.000+03:00');

insert into eats_rest_menu_storage.place_menu_category_statuses (
    place_menu_category_id, active, updated_at
) values
    (1, true, '2020-01-01T01:01:01.000+03:00'),
    (2, true, '2020-01-01T01:01:01.000+03:00');
