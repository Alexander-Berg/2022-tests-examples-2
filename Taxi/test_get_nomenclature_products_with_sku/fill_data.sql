insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; -- active for place 1
insert into eats_nomenclature.assortments default values; -- active for place 1 and trait_id = 1
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_1');
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id, trait_id)
values (1, 1, null, null), (1, 2, null, 1);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 1, '11111111111111111111111111111111'),
       ('item_origin_2', 'def', 2, 1, 'Сок U! Ананасовый', 1.0, 1, 1000, true, true, true, 1, '22222222-2222-2222-2222-222222222222'),
       ('item_origin_3', 'ghi', 2, 2, 'Печенье детское Органик Яблочный мармелад 18 мес. Alpine', 1.0, 2, 1, false, true, true, 1, '33333333-3333-3333-3333-333333333333'),
       ('item_origin_4', 'jkl', 3, 2, 'Печенье Fleur Alpine с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444444'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, false, true, 1, '55555555555555555555555555555555'),
       ('item_origin_6', 'jkl', 3, 2, 'Майонез', 1.0, 1, 50, true, true, false, 1, '66666666-6666-6666-6666-666666666666');

insert into eats_nomenclature.places_products(place_id, product_id, origin_id, price, old_price, vat, available_from)
values (1, 1, 'item_origin_1', 999, null, null, null),
       (1, 2, 'item_origin_2', 999, 999, 10, now()),
       (1, 3, 'item_origin_3', 999, 1000, 20, '2017-01-08 04:05:06'),
       (1, 4, 'item_origin_4', 999, 1000, 40, '2020-09-04 14:27:48.607413'),
       (1, 5, 'item_origin_5', 999, null, null, null),
       (1, 6, 'item_origin_6', 999, 1000, 40, '2020-09-04 14:27:48.607413');

insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values
       (1, 'category_1', 'category_1_origin');

insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', null, null),
       ('url_3', 'processed_url_3', '3'),
       ('url_4', 'processed_url_4', '4'),
       ('url_5', 'processed_url_5', '5');

insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX000', 9, 3);

insert into eats_nomenclature.categories_products (assortment_id, category_id, product_id, sort_order)
values (1, 1, 1, 100),
       (1, 1, 2, 50),
       (1, 1, 3, 10),
       (1, 1, 4, 100),
       (1, 1, 5, 20),
       (1, 1, 6, 100);

insert into eats_nomenclature.product_pictures (product_id, picture_id, updated_at)
values (3, 1, '2017-01-08 04:05:06+03:00'),
       (4, 2, '2017-01-08 04:05:06+03:00');

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (1, 3),
       (2, 1),
       (3, 2),
       (4, 1),
       (5, 3);

insert into eats_nomenclature.categories_relations (assortment_id, category_id, sort_order, parent_category_id)
values (1, 1, 100, null);
