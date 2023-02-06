delete from eats_nomenclature.categories_relations;

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values (1, 1, 100, 6),
       (1, 2, 100, 1),
       (1, 3, 100, 2),
       (1, 4, 100, null),
       (1, 6, 100, null);
