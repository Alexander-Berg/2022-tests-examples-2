insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug, stock_reset_limit) values (1, 'slug', 5);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; 
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, null);

insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, yt_updated_at)
values  (1,
         'Состав с МК 1',
         'Хранить МК 1',
         'f4e3f17d-607c-47a3-9235-3e883b048001',
         'Имя с МК 1',
         '2019-11-16 14:20:16.653015+0000'
        ),
        (2,
         'Состав с МК 2',
         'Хранить МК 2',
         'f4e3f17d-607c-47a3-9235-3e883b048002',
         'Имя с МК 2',
         '2019-11-16 14:20:16.653015+0000');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (1, '1', '1', 1, '1', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 1),
       (2, '2', '2', 1, '2', 0.1, 1, 100, true, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 2);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, available_from)
values (1, 1, '1', 999, '2017-01-08 04:05:06'),
       (1, 2, '2', 999, '2017-01-08 04:05:06'); 

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, null),
       (2, null);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1'),
       (22, '2'),
       (33, '3'),
       (44, '4');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base)
values (1, 11, 1, '1', '1_origin', false, false),
       (2, 22, 1, '2', '2_origin', false, false),
       (3, 33, 1, '3', '3_origin', false, false),
       (4, 44, 1, '4', '4_origin', false, false);

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
