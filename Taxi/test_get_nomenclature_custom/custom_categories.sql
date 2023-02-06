insert into eats_nomenclature.custom_categories(name, picture_id, external_id)
values ('custom_category_1', 1, 1),
       ('custom_category_2', 1, 2),
       ('custom_category_3', 1, 3),
       ('custom_category_4', 1, 4),
       ('custom_category_5', 1, 5);

insert into eats_nomenclature.categories(assortment_id, name, origin_id, is_custom, is_base, is_restaurant, custom_category_id)
values (1, 'category_8', 'category_8_origin', true, false, false, 1),
       (1, 'category_9', 'category_9_origin', true, false, false, 2),
       (1, 'category_10', 'category_10_origin', true, false, false, 3),
       (1, 'category_11', 'category_11_origin', true, true, false, 4),
       (1, 'category_12', 'category_12_origin', true, false, true, 4);

insert into eats_nomenclature.categories_relations(assortment_id, category_id, parent_category_id, sort_order)
values (1, 8, 1, 200),
       (1, 9, 1, 300),
       (1, 10, 1, 400),
       (1, 11, 1, 400),
       (1, 12, 1, 400);
