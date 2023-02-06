-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true);
insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 1);
insert into eats_nomenclature.assortments default values; -- active for place = 1 and trait = 1
insert into eats_nomenclature.assortments default values; -- active for place = 1 and trait = null
insert into eats_nomenclature.assortments default values; -- inactive for place = 1 and trait_id = 2
insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1'), (777, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 2, null, null), (1, null, 3, 2);

-- Products
insert into eats_nomenclature.products (origin_id, shipping_type_id, name, quantum, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 1, 'item_1', 0.2, false, false, 777, '11111111111111111111111111111111'),
       ('item_origin_2', 2, 'item_2', 1.0, true, true, 777, '22222222222222222222222222222222'),
       ('item_origin_3', 2, 'item_3', 1.0, false, true, 777, '33333333333333333333333333333333'),
       ('item_origin_4', 3, 'item_4', 1.0, true, false, 777, '44444444444444444444444444444444'),
       ('item_origin_5', 3, 'item_5', 0.5, true, true, 777, '55555555555555555555555555555555');

-- Custom categories and product types
insert into eats_nomenclature.custom_categories (id, name, external_id)
values
       (1, 'base_custom_category_1', 1),
       (2, 'base_custom_category_2', 2),
       (3, 'base_custom_category_3', 3),
       (4, 'promo_custom_category_4', 4),
       (5, 'base_custom_category_7', 5);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, 'value_uuid_1', 'молоко'), 
       (2, 'value_uuid_2', 'мороженое'), 
       (3, 'value_uuid_3', 'эскимо'), 
       (4, 'value_uuid_4', 'говядина');

insert into eats_nomenclature.custom_categories_product_types (custom_category_id, product_type_id)
values (2, 1),
       (2, 2),
       (3, 3),
       (3, 4);

-- Categories
insert into eats_nomenclature.categories_dictionary (id, name)
values
       (1, 'base_custom_category_1'),
       (2, 'base_custom_category_2'),
       (3, 'base_custom_category_3'),
       (4, 'promo_custom_category_4'),
       (5, 'base_partner_category_5'),
       (6, 'base_partner_category_6'),
       (7, 'base_custom_category_7');

insert into eats_nomenclature.categories (assortment_id, name, public_id, is_base, is_custom, custom_category_id)
values
       (1, 'base_custom_category_1', 1, true, true, 1),
       (1, 'base_custom_category_2', 2, true, true, 2),
       (1, 'base_custom_category_3', 3, true, true, 3),
       (1, 'promo_custom_category_4', 4, false, true, 4),
       (2, 'base_partner_category_5', 5, true, false, null),
       (2, 'base_partner_category_6', 6, true, false, null),
       (3, 'base_custom_category_7', 7, true, true, 5);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 2, 1),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 4, 5),
       (2, 6, 1),
       (2, 6, 2),
       (2, 6, 3),
       (3, 7, 1),
       (3, 7, 2),
       (3, 7, 3);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values (1, 1, null),
       (1, 2, 1),
       (1, 3, 1),
       (1, 4, null),
       (2, 5, null),
       (2, 6, 5),
       (3, 7, null);

insert into eats_nomenclature.pictures (url, processed_url)
values ('url_1', 'processed_url_1'),
       ('url_2', 'processed_url_2'),
       ('url_3', 'processed_url_3'),
       ('url_4', 'processed_url_4'),
       ('url_5', 'processed_url_5');

insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 2, 2),
       (1, 3, 3),
       (1, 4, 4),
       (1, 4, 5),
       (2, 5, 1),
       (2, 5, 2);

insert into eats_nomenclature.tags (id, name)
values (default, 'Тег 1'),
       (default, 'Тег 2'),
       (default, 'Тег 3');

insert into eats_nomenclature.custom_category_tags(custom_category_id, tag_id)
values (1, 1),
       (2, 2),
       (2, 3),
       (3, 1),
       (3, 3);
