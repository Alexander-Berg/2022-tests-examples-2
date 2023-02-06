insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id)
values (1, 'item_origin_1', 'abc', 1, 'item_1', 1.0, 1, 1000, false, false, true, 1, '11111111-1111-1111-1111-111111111111', null),
       (2, 'item_origin_2', 'def', 2, 'item_2', 1.0, 1, 1000, false, false, true, 1, '22222222-2222-2222-2222-222222222222', null);

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 1, 'item_origin_1', 999, null, null, null),
       (1, 2, 'item_origin_2', 999, null, null, null);

insert into eats_nomenclature.product_processing_types (id, value, value_uuid)
values (1, 'охлажденный', 0);

insert into eats_nomenclature.product_attributes(product_id, product_processing_type_id)
values (1, 1),
       (2, 1);
