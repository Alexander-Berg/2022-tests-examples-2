-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (1), (2);
insert into eats_nomenclature.places (id, slug) values (1, 'slug'), (2, 'new_slug');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1), (2, 2);

-- sku
insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, volume, yt_updated_at, сarbohydrates, proteins, fats, calories, expiration_info, is_alcohol, is_fresh, is_adult, alco_grape_cultivar, alco_flavour, alco_aroma, alco_pairing)
values ( 1,
         'Состав1',
         ('Хранить в сухом месте при температуре не более +25°С'),
         'f4e3f17d-607c-47a3-9235-3e883b048276',
         'Альтернативное имя1',
         11,
         '2019-11-16 14:20:16.653015+0000', '11.1', '12.2', '13.3', '111.1 ккал', '100 д', true, false, null, null, null, null, null),
       ( 2,
        'Состав2',
        ('Хранить в сухом месте при температуре не более +5°С'),
        '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
        'Альтернативное имя2',
        22,
        '2019-11-16 14:20:16.653015+0000', '22 г', '23 г', '24 г', '222.2 ккал', '200 д', null, false, null, 
        'Не должно попасть в описание', 'Не должно попасть в описание', 'Не должно попасть в описание', 'Не должно попасть в описание'),
       ( 3,
        'Состав3',
        ('Хранить в сухом месте при температуре не более +5°С'),
        '33333333-37d2-44ae-8479-ae0d700c4ecd',
        'Альтернативное имя3',
        33,
        '2019-11-16 14:20:16.653015+0000', '22 г', '23 г', '24 г', '222.2 ккал', '200 д', true, null, false, null, null, null, null),
        ( 4,
        'Состав4',
        ('Хранить в сухом месте при температуре не более +5°С'),
        '44444444-37d2-44ae-8479-ae0d700c4ecd',
        'Альтернативное имя4',
        44,
        '2019-11-16 14:20:16.653015+0000', '22 г', '23 г', '24 г', '222.2 ккал', '200 д', null, null, true, null, null, null, null),
        ( 5,
        'Состав5',
        ('Хранить в сухом месте при температуре не более +5°С'),
        '55555555-37d2-44ae-8479-ae0d700c4ecd',
        'Альтернативное имя5',
        55,
        '2019-11-16 14:20:16.653015+0000', '22 г', '23 г', '24 г', '222.2 ккал', '200 д', true, null, null, 'Сорт', 'Вкус', 'Аромат', 'Пейринг');
alter sequence eats_nomenclature.sku_id_seq restart with 50;

insert into eats_nomenclature.product_types (id, value_uuid, value)
values  (1, '3df0d4be-644f-5a23-b912-5e6f29fe53c2', 'Печенье детское'),
        (2, '2220d4be-644f-5a23-b912-5e6f29fe53c2', 'Молоко'),
        (3, '3330d4be-644f-5a23-b912-5e6f29fe53c2', 'Творог'),
        (4, '4440d4be-644f-5a23-b912-5e6f29fe53c2', 'Яблоки');
alter sequence eats_nomenclature.product_types_id_seq restart with 50;

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values  (2, '40a7405a-84f7-5468-99c5-94d91a2e0100', 'Fleur Alpine');

insert into eats_nomenclature.product_processing_types (id, value, value_uuid)
values (1, 'охлажденный', 0),
       (2, 'замороженный', 1),
       (3, 'без обработки', 2);

insert into eats_nomenclature.sku_attributes (sku_id, product_brand_id, product_processing_type_id, product_type_id)
values  (1, 2, 2, 1),
        (2, 2, 1, 2),
        (4, null, null, 4),
        (5, 2, null, null);

-- Items
insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), 
       ('vendor_2', 'country_2'), 
       ('vendor_3', 'country_3'), 
       ('vendor_4', '');

alter sequence eats_nomenclature.products_id_seq restart with 401;

insert into eats_nomenclature.marking_types(value)
values
    ('default'),
    ('energy_drink');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, volume_unit_id, volume_value, adult, is_catch_weight, is_choosable, brand_id, public_id, sku_id, package_info, marking_type_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 1.0, 1, 100, 1, 10, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 1, 'Пакет', 1),
       ('item_origin_2', 'def', 2, 1, 'item_2', 1.0, 2, 200, 2, 20, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 2, 'Пакет', 1),
       ('item_origin_3', 'ghi', 2, 2, 'item_3', 1.0, 3, 300, null, null, null, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', null, 'Пакет', 1),
       ('item_origin_4', 'jkl', 3, 4, 'item_4', 1.0, 4, 400, null, null, null, true, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', null, 'Пакет', 2),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.0, null, null, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005', null, null, 2),
       ('item_origin_6', 'pqr', 3, 3, 'item_6', 0.0, null, null, null, null, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006', null, null, 2),
       ('item_origin_7', 'mno', 3, 3, 'item_7', 0.0, null, null, null, null, true, true, false, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', null, null, null),
       ('item_origin_8', 'mno', 3, 3, 'item_8', 0.0, null, null, null, null, true, true, false, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008', null, null, null),
       ('item_origin_9', 'abc', 1, 1, 'item_9', 1.0, 1, 100, 1, 10, false, false, true, 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009', 3, null, null),
       ('item_origin_10', 'abc', 1, 1, 'item_10', 1.0, 1, 100, 1, 10, false, false, true, 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010', 5, null, null);

insert into eats_nomenclature.product_attributes(product_id, product_processing_type_id, product_type_id)
values (401, 1, 4),
       (402, 2, 1),
       (403, 3, 3);

insert into eats_nomenclature.overriden_product_attributes(product_id, product_type_id)
values (401, 3),
       (402, 2),
       (403, 1);

-- Picture
insert into eats_nomenclature.pictures (url, processed_url, hash)
values ('url_1', 'processed_url_1', '1'),
       ('url_2', null, null),
       ('url_3', 'processed_url_3', '3');

insert into eats_nomenclature.product_pictures (product_id, picture_id, updated_at)
values (401, 3, '2017-01-08 04:05:06+03:00'),
       (402, 3, '2017-01-08 04:05:06+03:00'),
       (403, 3, '2017-01-08 04:05:06+03:00');

insert into eats_nomenclature.sku_pictures (sku_id, picture_id)
values  (1, 1);

-- Barcode
-- uq: value+type_id+weight_encoding_id
insert into eats_nomenclature.barcodes(unique_key, value, barcode_type_id, barcode_weight_encoding_id)
values ('123ETR45611', '123ETR456', 1, 1),
       ('999UUU42', '999UUU', 4, 2),
       ('XXX00093', 'XXX000', 9, 3);

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (401, 3),
       (402, 3),
       (403, 2),
       (403, 3),
       (404, 1),
       (405, 3),
       (406, 3);
