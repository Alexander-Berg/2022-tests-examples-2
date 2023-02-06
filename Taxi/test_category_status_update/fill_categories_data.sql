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
        '44444444-4444-4444-4444-444444444444', 1,
        'category_origin_id_4', 'category_name_4'
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1,
        'category_origin_id_5', 'category_name_5'
    ),
    (
        '66666666-6666-6666-6666-666666666666', 1,
        'category_origin_id_6', 'category_name_6'
    ),
    (
        '77777777-7777-7777-7777-777777777777', 1,
        'category_origin_id_7', 'category_name_7'
    );

insert into eats_rest_menu_storage.place_menu_categories (
    brand_menu_category_id, place_id, origin_id, sort,
    legacy_id, name, schedule, deleted_at
) values
    (
        '11111111-1111-1111-1111-111111111111', 1,
        'category_origin_id_1', 1, 1, null, null, null
    ),
    (
        '22222222-2222-2222-2222-222222222222', 1,
        'category_origin_id_2', 1, 1, null, null, null
    ),
    (
        '33333333-3333-3333-3333-333333333333', 1,
        'category_origin_id_3', 1, 1, null, null, null
    ),
    (
        '44444444-4444-4444-4444-444444444444', 1,
        'category_origin_id_4', 1, 1, null, null, null
    ),
    (
        '55555555-5555-5555-5555-555555555555', 1,
        'category_origin_id_5', 1, 1, null, null, null
    ),
    (
        '66666666-6666-6666-6666-666666666666', 1,
        'category_origin_id_6', 1, 1, null, null, null
    ),
    (
        '77777777-7777-7777-7777-777777777777', 1,
        'category_origin_id_7', 1, 1, null, null, now()
    );
 
insert into eats_rest_menu_storage.place_menu_category_statuses (
    place_menu_category_id, active, deactivated_at, reactivate_at, updated_at, deleted_at
) values
    (1, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', '2020-12-01T00:00:00+00:00', null),
    (2, false, '2020-12-01T00:00:00+00:00', '2020-12-30T00:00:00+00:00', '2020-12-01T00:00:00+00:00', '2020-12-01T00:00:00+00:00'),
    (3, true, null, null, '2020-12-01T00:00:00+00:00', null),
    (4, true, null, null, '2020-12-01T00:00:00+00:00', null);
