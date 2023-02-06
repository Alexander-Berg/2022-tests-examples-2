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
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'item_origin_id_3',
        'name3', true, 'description3', 20.0, 2
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'item_origin_id_4',
        'name4', true, 'description4', 20.0, 2
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1, 'item_origin_id_5',
        'name5', true, 'description5', 20.0, 2
    ),
    (
        '66666666-6666-6666-6666-666666666666', 1, 'item_origin_id_6',
        'name6', true, 'description6', 20.0, 2
    ),
    (
        '77777777-7777-7777-7777-777777777777', 1, 'item_origin_id_7',
        'name7', true, 'description7', 20.0, 2
    );

insert into eats_rest_menu_storage.place_menu_items (
    brand_menu_item_id, place_id, origin_id, name, adult,
    description, weight_value, weight_unit, sort, shipping_types,
    legacy_id, ordinary, choosable, deleted_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1, 'item_origin_id_1',
        'name1', null, null, null, null, 100, '{delivery,pickup}', 1, true, true, null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1, 'item_origin_id_2',
        'name2', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1, 'item_origin_id_3',
        'name3', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1, 'item_origin_id_4',
        'name4', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1, 'item_origin_id_5',
        'name5', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null
    ),
    (
        '66666666-6666-6666-6666-666666666666', 1, 'item_origin_id_6',
        'name6', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, false, null
    ),
    (
        '77777777-7777-7777-7777-777777777777', 1, 'item_origin_id_7',
        'name7', false, 'other_description2', null, null, 200, '{delivery}', 2,
        true, true, now()
    );

insert into eats_rest_menu_storage.place_menu_item_statuses (
    place_menu_item_id, active, deactivated_at, reactivate_at, updated_at, deleted_at
) values
    (1, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', '2020-12-01T00:00:00+00:00', null),
    (2, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', '2020-12-01T00:00:00+00:00', '2020-12-01T00:00:00+00:00'),
    (3, true, null, null, '2020-12-01T00:00:00+00:00', null),
    (4, true, null, null, '2020-12-01T00:00:00+00:00', null);
