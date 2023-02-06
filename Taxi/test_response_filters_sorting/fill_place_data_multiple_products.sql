insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug, stock_reset_limit) values (1, 'slug', 5);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; 
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, null);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values  (1, '40a7405a-84f7-5468-99c5-94d91a2e0001', '11.1'),
        (2, '40a7405a-84f7-5468-99c5-94d91a2e0002', '22.2'),
        (3, '40a7405a-84f7-5468-99c5-94d91a2e0003', '33.3');

insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, merged_to_uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, expiration_info, volume, yt_updated_at, is_adult, is_alcohol)
values  (1,
         'Состав с МК 1',
         'Хранить МК 1',
         'f4e3f17d-607c-47a3-9235-3e883b048001',
         null,
         'Имя с МК 1',
         '101 г',
         '102 г',
         '103 г',
         '104 г',
         '105 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         false,
         true),
        (2,
         'Состав с МК 2',
         'Хранить МК 2',
         'f4e3f17d-607c-47a3-9235-3e883b048002',
         null,
         'Имя с МК 2',
         '251 г',
         '252 г',
         '253 г',
         '254 г',
         '255 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         null,
         null),
        (3,
         'Состав с МК 3',
         'Хранить МК 3',
         'f4e3f17d-607c-47a3-9235-3e883b048003',
         null,
         'Имя с МК 3',
         '351 г',
         '352 г',
         '353 г',
         '354 г',
         '355 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         null,
         null),
         (4,
         'Состав с МК 4',
         'Хранить МК 4',
         'f4e3f17d-607c-47a3-9235-3e883b048004',
         null,
         'Имя с МК 4',
         '101 г',
         '102 г',
         '103 г',
         '104 г',
         '105 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         false,
         true),
        (5,
         'Состав с МК 5',
         'Хранить МК 5',
         'f4e3f17d-607c-47a3-9235-3e883b048005',
         null,
         'Имя с МК 5',
         '251 г',
         '252 г',
         '253 г',
         '254 г',
         '255 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         null,
         null),
        (6,
         'Состав с МК 6',
         'Хранить МК 6',
         'f4e3f17d-607c-47a3-9235-3e883b048006',
         null,
         'Имя с МК 6',
         '351 г',
         '352 г',
         '353 г',
         '354 г',
         '355 ккал',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         null,
         null);

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (1, '1', '1', 1, 1, '1', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 1),
       (2, '2', '2', 1, 1, '2', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 2),
       (3, '3', '3', 1, 1, '3', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 3),
       (4, '4', '4', 1, 1, '4', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 4),
       (5, '5', '5', 1, 1, '5', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005', 5),
       (6, '6', '6', 1, 1, '6', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006', 6);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat, force_unavailable_until)
values (1, 1, '1', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 2, '2', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 3, '3', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 4, '4', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 5, '5', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 6, '6', 999, null, null, null, '2017-01-08 04:05:06', 10, null); 

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, null),
       (2, null),
       (3, null),
       (4, null),
       (5, null),
       (6, null);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base)
values (1, 11, 1, '1', '1_origin', false, false);

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 1);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 1),
       (1, 1, 2, 1),
       (1, 1, 3, 1),
       (1, 1, 4, 1),
       (1, 1, 5, 1),
       (1, 1, 6, 1);
