insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_8', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008'),
       ('item_origin_8', 'abc', 1, 1, 'item_1', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69c008');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, force_unavailable_until)
values (2, 408, 'item_origin_8', '2020-01-01T12:00:00'),  -- old product_id from previous brand
       (2, 409, 'item_origin_8', '2020-01-01T12:00:00');
