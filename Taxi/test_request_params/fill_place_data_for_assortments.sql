insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug, stock_reset_limit) values (1, 'slug', 5);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 1
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 2
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = null
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1'), (1, 'assortment_name_2');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, 1), (1, 2, null, 2), (1, 3, null, null);
insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (1, 1);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.products (id, origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values (1, '1', '1', 1, 1, '1', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'),
       (2, '2', '2', 2, 1, '2', 0.0, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, available_from)
values (1, 1, '1', 999, '2017-01-08 04:05:06'), 
       (1, 2, '2', 999, '2017-01-08 04:05:06'); 

insert into eats_nomenclature.stocks (place_product_id, value)
values (1, null), 
       (2, null);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base)
values
       (1, 11, 1, '1', '1_origin', false, false),
       -- assortment 2
       (2, 11, 2, '1', '1_origin', false, false);

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 1),
       (2, 1, 2, 1);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3),
       -- assortment 2
       (2, null, 2, 45);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 100),
       -- assortment 2
       (2, 2, 2, 40);
