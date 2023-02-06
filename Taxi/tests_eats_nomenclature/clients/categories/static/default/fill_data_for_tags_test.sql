insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values (1, '1', '1', 1, null, '1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001');

insert into eats_nomenclature.pictures (id, url, processed_url, hash)
values (1, 'url_1', 'processed_url_1', '1');

insert into eats_nomenclature.tags (id, name)
values (default, 'Тег 1'),
       (default, 'Тег 2'),
       (default, 'Тег 3');

insert into eats_nomenclature.custom_categories(id, name, picture_id, description, external_id)
values (11, 'custom category 1', 1, 'abc', 1),
       (22, 'custom category 2', 1, 'def', 2),
       (33, 'custom category 3', 1, 'ghi', 3);

insert into eats_nomenclature.custom_category_tags(custom_category_id, tag_id)
values (22, 1),
       (22, 2),
       (33, 3);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1'),
       (22, '1_1'),
       (33, '1_1_1');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base, custom_category_id)
values
       (1, 11, 1, '1', '1_origin', true, true, 11),
       (2, 22, 1, '1_1', '1_1_origin', true, true, 22),
       (3, 33, 1, '1_1_1', '1_1_1_origin', true, true, 33);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3),
       (2, 1, 1, 5),
       (3, 2, 1, 6);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 3, 1, 100);

insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1),
       (1, 2, 1);
