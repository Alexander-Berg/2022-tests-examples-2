insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug, stock_reset_limit) values (1, 'slug', 5);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, null);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values (1, '1', null, 1, 1, '1', 0.1, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, full_price, old_full_price, available_from, vat, force_unavailable_until)
values (1, 1, '1', 999, null, null, null, '2017-01-08 04:05:06', 10, null);

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, 10);

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

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 1),
       (1, 2, 1, 1),
       (1, 3, 1, 1),
       (1, 4, 1, 1);

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 1),
       (1, 1, 2, 1),
       (1, 1, 3, 1),
       (1, 1, 4, 1);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 100),
       (2, null, 1, 100),
       (3, null, 1, 100),
       (4, null, 1, 100);
