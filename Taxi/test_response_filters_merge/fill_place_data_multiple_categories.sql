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
        (2, '40a7405a-84f7-5468-99c5-94d91a2e0002', '22.2');

insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, merged_to_uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, country, package_type, expiration_info, volume, yt_updated_at, is_adult, is_alcohol)
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
         'Бельгия',
         'Картонная коробка',
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
         '101 г',
         '102 г',
         '103 г',
         '104 г',
         '105 ккал',
         'Бельгия',
         'Картонная коробка',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000',
         false,
         true);

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (1, '1', '1', 1, 1, '1', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 1),
       (2, '2', '2', 1, 1, '2', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 2);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat, force_unavailable_until)
values (1, 1, '1', 999, null, null, null, '2017-01-08 04:05:06', 10, null),
       (1, 2, '2', 999, null, null, null, '2017-01-08 04:05:06', 10, null); 

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, null),
       (2, null);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1'),
       (22, '2'),
       (33, '3'),
       (44, '4');

insert into eats_nomenclature.tags (id, name)
values (default, 'Тег 1'),
       (default, 'Тег 2'),
       (default, 'Тег 3'),
       (default, 'Тег 4');

insert into eats_nomenclature.custom_categories(id, name, description, external_id)
values (11, 'custom category 1', 'abc', 1),
       (22, 'custom category 2', 'abc', 2),
       (33, 'custom category 3', 'abc', 3),
       (44, 'custom category 4', 'abc', 4);

insert into eats_nomenclature.custom_category_tags(custom_category_id, tag_id)
values (11, 1),
       (22, 1),
       (33, 1),
       (44, 1);

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base, custom_category_id)
values (1, 11, 1, '1', '1_origin', false, false, 11),
       (2, 22, 1, '2', '2_origin', false, false, 22),
       (3, 33, 1, '3', '3_origin', false, false, 33),
       (4, 44, 1, '4', '4_origin', false, false, 44);

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 1),
       (1, 1, 2, 1),
       (1, 1, 3, 1),
       (1, 1, 4, 1);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3),
       (2, 1, 1, 4),
       (3, 1, 1, 5),
       (4, 2, 1, 6);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 3, 1, 1),
       (1, 4, 2, 1);
