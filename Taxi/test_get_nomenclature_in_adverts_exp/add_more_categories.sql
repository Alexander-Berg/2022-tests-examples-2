-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values (1, 'category_8', 'category_8_origin'),
       (1, 'category_9', 'category_9_origin');

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id, sort_order, parent_category_id)
values (1, 8, 100, 1),
       (1, 9, 100, 4);
