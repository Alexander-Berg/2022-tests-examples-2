insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, 'place_1', true);

insert into eats_nomenclature.brand_places (brand_id, place_id)
values (1, 1);

insert into eats_nomenclature.assortments
values (1);

insert into eats_nomenclature.place_assortments (place_id, assortment_id)
values (1, 1);

insert into eats_nomenclature.sku (id, uuid, alternate_name)
values (1, '00000000-0000-0000-0000-000000000000', 'sku_match'),
       (2, '00000000-0000-0000-0000-000000000001', 'sku_match_different'),
       (3, '00000000-0000-0000-0000-000000000002', 'sku_mismatch');

insert into eats_nomenclature.products (id, sku_id, origin_id, name, public_id, quantum, measure_unit_id, measure_value, volume_unit_id, volume_value, brand_id)
values (1, null, 'origin_1', 'name1', '11111111-1111-1111-1111-111111111111', 1, null, null, null, null, 1),
       (2, null, 'origin_2', 'name2', '22222222-2222-2222-2222-222222222222', 1, null, null, null, null, 1),
       (3, null, 'origin_3', 'name3', '33333333-3333-3333-3333-333333333333', 1, null, null, null, null, 1);

insert into eats_nomenclature.products_usage (product_id, last_referenced_at)
values (1, '2021-09-30T14:00:00'),
       (2, '2021-09-30T14:00:00'),
       (3, '2021-09-30T14:00:00');

insert into eats_nomenclature.categories (id, assortment_id, name, origin_id)
values
    (1, 1, 'Корневая категория 1', 'origin_1'),
    (2, 1, 'Корневая категория 2', 'origin_2'),
    (3, 1, 'Подкатегория 11', 'origin_3');

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id)
values (1, 2, 2),
       (1, 3, 3);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, parent_category_id)
values (1, 1, null),
       (1, 2, null),
       (1, 3, 1);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, '00000000-0000-0000-0000-000000000001', 'Тип товара');

insert into eats_nomenclature.product_attributes (product_id, product_type_id)
values (1, 1),
       (2, 1),
       (3, 1);
