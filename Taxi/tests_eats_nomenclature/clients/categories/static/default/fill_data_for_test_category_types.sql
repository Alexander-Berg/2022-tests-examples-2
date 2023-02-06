insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.place_assortments (place_id, assortment_id)
values (1, 1);

insert into eats_nomenclature.custom_categories(id, name, description, external_id)
values (11, 'custom category 1', 'abc', 1),
       (22, 'custom category 2', 'def', 2),
       (33, 'custom category 3', 'def', 3),
       (44, 'custom category 4', 'def', 4);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1'),
       (22, '2'),
       (33, '3'),
       (44, '4');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base, is_restaurant, custom_category_id)
values
    (1, 11, 1, '1', '1_origin', false, false, false, 11),
    (2, 22, 1, '2', '2_origin', true, false, false, 22),
    (3, 33, 1, '3', '3_origin', true, true, false, 33),
    (4, 44, 1, '3', '4_origin', true, false, true, 44);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 100),
       (2, null, 1, 100),
       (3, null, 1, 100),
       (4, null, 1, 100);
