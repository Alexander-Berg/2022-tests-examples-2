insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, country, package_type, expiration_info, yt_updated_at)
values (1,
        '2',
        '3',
        'f4e3f17d-607c-47a3-9235-3e883b048276',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        '11',
        '12',
        '13',
        '2018-01-01 14:20:16+0000'
        ), 
        (2,
               '2',
               '3',
               '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
               '5',
               '6',
               '7',
               '8',
               '9',
               '10',
               '11',
               '12',
               '13',
               '2018-01-01 14:20:16+0000'),
               (3,
               '2',
               '3',
               'd5030921-d507-43d9-b234-f316fbcf62be',
               '5',
               '6',
               '7',
               '8',
               '9',
               '10',
               '11',
               '12',
               '13',
               '2018-01-01 14:20:16+0000');
alter sequence eats_nomenclature.sku_id_seq restart with 50;

insert into eats_nomenclature.pictures (id, url, processed_url)
values  (1, 'url_1', 'processed_url_1'),
        (2, 'url_2', null);
alter sequence eats_nomenclature.pictures_id_seq restart with 50;

insert into eats_nomenclature.sku_pictures (sku_id, picture_id, retailer_name)
values  (2, 1, 'retailer_name_1'),
        (2, 1, 'retailer_name_2'),
        (2, 1, null),
        (1, 2, 'retailer_name_1'),
        (1, 2, 'retailer_name_2'),
        (1, 2, null);

insert into eats_nomenclature.barcodes (id, unique_key, value)
values  (1, 'barcode_1', 'barcode_1'),
        (2, 'barcode_2', 'barcode_2');
alter sequence eats_nomenclature.barcodes_id_seq restart with 50;

insert into eats_nomenclature.sku_barcodes (sku_id, barcode_id)
values  (2, 1),
        (1, 2);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values  (1, '3df0d4be-644f-5a23-b912-5e6f29fe53c2', 'Печенье детское'),
        (2, '1d6b32ec-430f-5980-8146-f66e2a679d7c', 'Майонез');
alter sequence eats_nomenclature.product_types_id_seq restart with 50;

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values  (1, '40a7405a-84f7-5468-99c5-94d91a2e0100', 'value_1'),
        (2, '7116a9b1-5759-531a-a3c5-ec1e9a69c863', 'value_2');
alter sequence eats_nomenclature.product_brands_id_seq restart with 50;

insert into eats_nomenclature.product_processing_types (id, value_uuid, value)
values  (1, '020222a2-e9a9-41ff-a399-9bf15aea8bd2', 'value_1'),
        (2, '1a8db2fe-03fd-409d-b7df-39c8b76e01eb', 'value_2');
alter sequence eats_nomenclature.product_processing_types_id_seq restart with 50;

insert into eats_nomenclature.sku_attributes (sku_id, product_brand_id, product_type_id, product_processing_type_id)
values  (1, 1, 1, 1),
        (2, 1, 1, 1),
        (3, 2, 2, 2);
