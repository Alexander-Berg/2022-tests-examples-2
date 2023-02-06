-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (2);
insert into eats_nomenclature.places (id, slug) values (2, 'slug2');
insert into eats_nomenclature.assortments default values; -- inactive for place 2
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (2, null, 2);

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_11', 'abc', 1, 1, 'item_10', 0.0, null, null, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010');


insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 413, 'item_origin_11', 999, 1000, 40, '2020-09-04 14:27:48.607413');

-- Category
insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values (2, 'category_11', 'category_11_origin');

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_11', 'processed_url_11', '11');

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR456011', '123ETR4560', 1, 1);

-- Category Products
insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (2, 7, 413, 100);

insert into eats_nomenclature.product_pictures (product_id, picture_id)
values (413, 3);

-- Category Pictures
insert into eats_nomenclature.category_pictures (assortment_id, category_id, picture_id)
values (2, 7, 3);

-- Place Product Barcodes
insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (413, 3);

-- Category Relations
insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order, parent_category_id)
values (2, 7, 100, 7);

-- Stock
update eats_nomenclature.stocks 
set value = 20 
where place_product_id = 33;
