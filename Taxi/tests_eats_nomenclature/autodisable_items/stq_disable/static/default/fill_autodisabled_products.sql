insert into eats_nomenclature.not_picked_items(place_id, product_id, origin_id, quantity_requested, quantity_picked, created_at)
values
    -- item_origin_1
    (1, 401, 'item_origin_1', 10, 5, '2021-09-28T15:00:00'),  -- before check period - not taken into count
    (1, 401, 'item_origin_1', 11, 4, '2021-09-30T04:00:00'),  -- in check period, but before force_unavailable_until - not taken
    (1, 401, 'item_origin_1', 12, 3, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    -- item_origin_2
    (1, 402, 'item_origin_2', 17, 6, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    -- item_origin_3
    (1, 403, 'item_origin_3', 20, 9, '2021-09-30T06:00:00'),  -- in check period and never was disabled - taken
    (1, 403, 'item_origin_3', 18, 0, '2021-09-30T12:00:00'),  -- in check period and never was disabled - taken
    -- item_origin_4
    (1, 404, 'item_origin_4', 17, 6, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    (1, 404, 'item_origin_4', 13, 3, '2021-09-30T13:00:00'),  -- in check period and after force_unavailable_until - taken
    -- item_origin_5
    (1, 405, 'item_origin_5', 15, 1, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    (1, 405, 'item_origin_5', 12, 1, '2021-09-30T14:00:00'),  -- in check period and after force_unavailable_until - taken
    -- item_origin_6
    (2, 406, 'item_origin_6', 17, 2, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    (2, 406, 'item_origin_6', 18, 2, '2021-09-30T12:00:00'),  -- in check period and after force_unavailable_until - taken
    (2, 406, 'item_origin_6', 19, 2, '2021-09-30T13:00:00'),  -- in check period and after force_unavailable_until - taken
    (2, 406, 'item_origin_6', 20, 2, '2021-09-30T14:00:00'),  -- in check period and after force_unavailable_until - taken
    -- item_origin_7
    (1, 407, 'item_origin_7', 21, 3, '2021-09-30T06:00:00'),  -- in check period and after force_unavailable_until - taken
    (1, 407, 'item_origin_7', 22, 3, '2021-09-30T12:00:00'),  -- in check period and after force_unavailable_until - taken
    (1, 407, 'item_origin_7', 23, 3, '2021-09-30T13:00:00'),  -- in check period and after force_unavailable_until - taken
    (1, 407, 'item_origin_7', 24, 3, '2021-09-30T14:00:00');  -- in check period and after force_unavailable_until - taken

insert into eats_nomenclature.autodisabled_products(place_id, product_id, disabled_count, last_disabled_at, need_recalculation)
values (1, 401, 1, '2021-09-29T17:00:00', false),
       (1, 402, 2, '2021-09-27T05:00:00', false),
       (1, 404, 2, '2020-01-01T00:00:00', false),
       (1, 405, 6, '2020-01-01T00:00:00', false),
       (2, 406, 2, '2020-01-01T00:00:00', false),
       (1, 407, 1, '2020-01-01T00:00:00', false);
