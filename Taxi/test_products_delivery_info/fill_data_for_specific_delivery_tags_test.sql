insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments(id) values (default),(default);
insert into eats_nomenclature.place_assortments(place_id, assortment_id) values (1, 1);
insert into eats_nomenclature.sku (id, uuid, alternate_name) values (1, 1, '1'), (2, 2, '2'), (3, 3, '3'), (4, 4, '4');
insert into eats_nomenclature.categories (id, assortment_id, name) values (1, 1, '1');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (1, 'item_origin_1', 'abc', 1, 'item_1', 1.0, 1, 1000, false, false, true, 1, '11111111-1111-1111-1111-111111111111', null),
       (2, 'item_origin_2', 'def', 2, 'item_2', 1.0, 1, 1000, false, false, true, 1, '22222222-2222-2222-2222-222222222222', 1),
       (3, 'item_origin_3', 'ghi', 2, 'item_3', 1.0, 1, 1000, false, false, true, 1, '33333333-3333-3333-3333-333333333333', null),
       (4, 'item_origin_4', 'jkl', 3, 'item_4', 1.0, 1, 1000, false, false, true, 1, '44444444-4444-4444-4444-444444444444', null),
       (5, 'item_origin_5', 'mno', 3, 'item_5', 1.0, 1, 1000, false, false, true, 1, '55555555-5555-5555-5555-555555555555', null);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id) values (1,1,1),(1,1,2),(1,1,3),(1,1,4),(1,1,5);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 1, 'item_origin_1', 999, null, null, null),
       (1, 2, 'item_origin_2', 999, null, null, null),
       (1, 3, 'item_origin_3', 999, null, null, null),
       (1, 4, 'item_origin_4', 999, null, null, null),
       (1, 5, 'item_origin_5', 999, null, null, null);

insert into eats_nomenclature.product_processing_types (id, value, value_uuid)
values (1, 'охлажденный', 0);

insert into eats_nomenclature.product_attributes(product_id, product_processing_type_id)
values (1, 1),
       (5, 1);

insert into eats_nomenclature.sku_attributes(sku_id, product_processing_type_id)
values (1, 1);
