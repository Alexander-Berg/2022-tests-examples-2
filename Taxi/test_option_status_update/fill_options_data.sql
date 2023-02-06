-- items
insert into eats_rest_menu_storage.brand_menu_items (
    id, brand_id, origin_id, name, adult,
    description, weight_value, weight_unit
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'item_origin_id_1',
        'name1', false, 'description1', 10.0, 1
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'item_origin_id_2',
        'name2', true, 'description2', 20.0, 2
    );

insert into eats_rest_menu_storage.place_menu_items (
    brand_menu_item_id, place_id, origin_id, name, adult,
    description, weight_value, weight_unit, sort, shipping_types,
    legacy_id, ordinary, choosable
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'item_origin_id_1',
        'name1', null, null, null, null, 100, '{delivery,pickup}', 1, true, true
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'item_origin_id_2',
        'name2', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false
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
    );


insert into eats_rest_menu_storage.place_menu_item_option_groups (
    brand_menu_item_option_group, place_menu_item_id, origin_id,
    legacy_id, name, sort, min_selected_options, max_selected_options
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'option_group_origin_id_1',
        1, 'other_option_group_name1', 10, 6, 11
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'option_group_origin_id_2',
        2, null, null, null, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 2, 'option_group_origin_id_3',
        3, null, 123, null, 100
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
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'option_origin_id_3',
        'option_name_3', 1, null, null, 2
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'option_origin_id_4',
        'option_name_4', 1, null, null, 2
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1, 'option_origin_id_5',
        'option_name_5', 1, null, null, 2
    ),
    (
        '66666666-6666-6666-6666-666666666666', 1, 'option_origin_id_6',
        'option_name_6', 1, null, null, 2
    ),
    (
        '77777777-7777-7777-7777-777777777777', 1, 'option_origin_id_7',
        'option_name_7', 1, null, null, 2
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
        '22222222-2222-2222-2222-222222222222', 1, 'option_origin_id_2',
        2, null, null, null, null, null, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 2, 'option_origin_id_3',
        2, null, null, null, null, null, null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 2, 'option_origin_id_4',
        2, null, null, null, null, null, null
    ),
    (
        '55555555-5555-5555-5555-555555555555', 3, 'option_origin_id_5',
        2, null, null, null, null, null, null
    ),
    (
        '66666666-6666-6666-6666-666666666666', 3, 'option_origin_id_6',
        2, null, null, null, null, null, null
    ),
    (
        '77777777-7777-7777-7777-777777777777', 3, 'option_origin_id_7',
        2, null, null, null, null, null, '2020-12-01T00:00:00+00:00'
    );

insert into eats_rest_menu_storage.place_menu_item_option_statuses (
    place_menu_item_option_id, active, deactivated_at, reactivate_at,
    deleted_at, updated_at
) values
    (1, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', null, '2020-12-30T00:00:00+00:00'),
    (2, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00'),
    (3, true, null, null, null, '2020-12-30T00:00:00+00:00'),
    (4, true, null, null, null, '2020-12-30T00:00:00+00:00');
