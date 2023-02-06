insert into eats_nomenclature.categories_dictionary (id, name)
values
       (1, 'category_1'),
       (2, 'category_2'),
       (3, 'category_3'),
       (4, 'category_4'),
       (5, 'category_5'),
       (6, 'category_6'),
       (7, 'category_7'),
       (8, 'category_8');

insert into eats_nomenclature.categories (assortment_id, name, public_id, is_base)
values
       (1, 'category_1', 1, true),
       (1, 'category_2', 2, true),
       (1, 'category_3', 3, true),
       (1, 'category_4', 4, true),
       (3, 'category_5', 5, true),
       (3, 'category_6', 6, true),
       (3, 'category_7', 7, false),
       (1, 'category_8', 8, false),
       (3, 'category_2', 2, true),
       (3, 'category_3', 3, true),
       (3, 'category_4', 4, true);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 1, 1),
       (1, 1, 2),
       (1, 4, 2),
       (1, 4, 3),
       (1, 8, 1),
       (1, 8, 2),
       (1, 1, 10), -- item_for_stock_limit_test
       (3, 6, 1),
       (3, 6, 2),
       (3, 7, 3),
       (3, 11, 2),
       (3, 11, 3);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values (1, 1, null),
       (1, 2, null),
       (1, 3, 2),
       (1, 4, 3),
       (1, 8, null),
       (3, 5, null),
       (3, 6, 5),
       (3, 7, null),
       (3, 9, null),
       (3, 10, 9),
       (3, 11, 10);
