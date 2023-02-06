insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, '1', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- inactive for place 1
insert into eats_nomenclature.assortments default values; -- active for place 1 with trait_id = 1
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, 2, null), (1, 3, null, 1);

insert into eats_nomenclature.vendors (name)
values ('vendor_1');

insert into eats_nomenclature.products (origin_id, vendor_id, name, brand_id)
values ('item_origin_1', 1, 'item_1', 777),
       ('item_origin_2', 1, 'item_2', 777),
       ('item_origin_3', 1, 'item_3', 777),
       ('item_origin_4', 1, 'item_4', 777),
       ('item_origin_5', 1, 'item_5', 777),
       ('item_origin_6', 1, 'item_5', 777);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price)
values (1, 1, 'item_origin_1', 999),
       (1, 2, 'item_origin_2', 999),
       (1, 3, 'item_origin_3', 999),
       (1, 4, 'item_origin_4', 999),
       (1, 5, 'item_origin_5', 999),
       (1, 6, 'item_origin_6', 999);

insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
(1, 'category_1', 'category_1_origin'),
(1, 'category_2', 'category_2_origin'),
(1, 'category_3', 'category_3_origin'),
(3, 'category_4', 'category_4_origin'),
(3, 'category_5', 'category_5_origin');

insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values
       -- trait_id = null
       (1, 1, 100, null),
       (1, 2, 100, null),
       (1, 3, 100, 1),
       -- trait_id = 1
       (3, 4, 100, null),
       (3, 5, 100, 4);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values
       -- trait_id = null
       (1, 1, 1, 100),
       (1, 1, 2, 100),
       (1, 1, 3, 100),
       (1, 2, 4, 100),
       (1, 2, 5, 100),
       (1, 3, 6, 100),
       -- trait_id = 1
       (3, 4, 4, 100),
       (3, 5, 5, 100),
       (3, 5, 6, 100);
