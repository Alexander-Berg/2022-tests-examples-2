insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, country, package_type, expiration_info, volume, yt_updated_at, is_adult, is_alcohol)
values ( 1,
         'Состав1',
         null,
         'f4e3f17d-607c-47a3-9235-3e883b048276',
         'Альтернативное имя1',
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         '2019-11-16 14:20:16.653015+0000',
        true,
        false), (2,
                                              'Состав2',
                                              null,
                                              '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
                                              'Альтернативное имя2',
                                              null,
                                              null,
                                              null,
                                              null,
                                              null,
                                              null,
                                              null,
                                              null,
                                              null,
                                              '2019-11-16 14:20:16.653015+0000',
                false,
                false),
       ( 3,
         'Состав3',
         null,
         'd5030921-d507-43d9-b234-f316fbcf62be',
         'Альтернативное имя3',
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         null,
         '2019-11-13 07:16:07.192982+0000',
        false,
        true);
alter sequence eats_nomenclature.sku_id_seq restart with 50;

insert into eats_nomenclature.pictures (id, url, processed_url)
values  (101, 'https://avatars.mds.yandex.net/get-edadeal/403310/723772bffc977ab631c11e23969fdbed/orig', 'https://avatars.mds.yandex.net/get-edadeal/403310/723772bffc977ab631c11e23969fdbed/orig'),
        (102, 'https://avatars.mds.yandex.net/get-edadeal/2421831/de9f1c29a090887d9b22864ddd51021d/orig', null);
alter sequence eats_nomenclature.pictures_id_seq restart with 50;

insert into eats_nomenclature.sku_pictures (sku_id, picture_id)
values  (1, 102),
        (2, 101);

insert into eats_nomenclature.barcodes (id, unique_key, value)
values  (101, '5412916940854', '5412916940854'),
        (102, '5412916941165', '5412916941165');
alter sequence eats_nomenclature.barcodes_id_seq restart with 50;

insert into eats_nomenclature.sku_barcodes (sku_id, barcode_id)
values  (1, 102),
        (2, 101);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values  (1, '3df0d4be-644f-5a23-b912-5e6f29fe53c2', 'Печенье детское');
alter sequence eats_nomenclature.product_types_id_seq restart with 50;

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values  (1, '40a7405a-84f7-5468-99c5-94d91a2e0100', 'Fleur Alpine');
alter sequence eats_nomenclature.product_brands_id_seq restart with 50;

insert into eats_nomenclature.sku_attributes (sku_id, product_brand_id, product_type_id)
values  (1, 1, 1),
        (2, 1, 1);

update eats_nomenclature.products
set sku_id = 1
where id = 413;

update eats_nomenclature.products
set sku_id = 2
where id = 403;

update eats_nomenclature.products
set sku_id = 3
where id = 402;
