-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, null);


-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1_available', 'desc', 1, 1, 'item_1', 0.0, 1, 10, false, false, true, 1, '11111111111111111111111111111111'),
       ('item_origin_2_force_unavailable', 'desc', 1, 1, 'item_2', 0.0, 2, 20, false, false, true, 1, '22222222222222222222222222222222');

insert into eats_nomenclature.places_products(id, place_id, product_id, origin_id, price, old_price, vat, available_from, force_unavailable_until)
values (31, 1, 401, 'item_origin_1_available', 999, null, null, now(), null),
       (32, 1, 402, 'item_origin_2_force_unavailable', 999, null, null, now(), null);
alter sequence eats_nomenclature.places_products_id_seq restart with 50;

-- Category
insert into eats_nomenclature.categories_dictionary(id, name)
values (1, 'category_1');

insert into eats_nomenclature.categories (assortment_id, name, origin_id, public_id)
values (1, 'category_1', 'category_1_origin', 1);

-- Places categories
insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values
    (1, 1, 1, 2);

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1');

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 401, 100),
       (1, 1, 402, 100);

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (401, 1),
       (402, 1);

-- Category Pictures
insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (1, 1, 1);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (401, 1),
       (402, 1);

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id, sort_order, parent_category_id)
values (1, 1, 100, null);

-- Stock
insert into eats_nomenclature.stocks (place_product_id, value)
values (31, 10),
       (32, 10);
