insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, merged_to_uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, country, package_type, expiration_info, volume, yt_updated_at)
values ( 1,
         'Яблочная паста (концентрированный яблочный сок, концентрированное яблочное  пюре, агент желирующий (пектин), регулятор кислотности (лимонная кислота)),  цельнозерновая пшеничная мука, концентрированный яблочный сок,  негидрогенизированные растительные масла (подсолнечное, кокосовое),  спельтовая мука, яйцо, молоко сухое обезжиренное, рисовая мука, натуральный  экстракт ванили, минералы морских водорослей (кальций, магний), разрыхлители  (карбонат аммония, гидрокарбонат натрия), витамин в1, антиокислитель  (токоферол).',
         'Хранить в сухом месте при температуре не более +25°С, относительной влажности воздуха не более 75%. Для детского питания печенье из открытого пакетика употребить в течение суток. ',
         'f4e3f17d-607c-47a3-9235-3e883b048276',
         null,
         'Печенье Fleur Alpine Яблочный мармелад, с 18-ти месяцев',
         '150 г',
         '65 г',
         '6.5 г',
         '11.8 г',
         '388 ккал',
         'Бельгия',
         'Картонная коробка',
         '300 д',
         null,
         '2019-11-16 14:20:16.653015+0000'), 
        (2,
                                'Концентрат яблочного сока (32%), цельнозерновая пшеничная мука, рисовая мука, негидрогенизированные растительные масла (подсолнечное, кокосовое), молоко сухое обезжиренное, разрыхлители (гидрокарбонат аммония, гидрокарбонат натрия), натуральный экстракт ванили, витамин в1, антиокислитель (токоферол).',
                                'Хранить в сухом месте ',
                                '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
                                null,
                                'Печенье Fleur Alpine с яблочным соком, с 6 месяцев',
                                '150 г',
                                '66.8 г',
                                '7.2 г',
                                '8.3 г',
                                '374 ккал',
                                'Бельгия',
                                'Картонная коробка',
                                '450 д',
                                null,
                                '2019-11-16 14:20:16.653015+0000'),
        (3, 
        'Масло подсолнечное рафинированное, вода, масло оливковое рафинированное, яичный желток, крахмал, соль, кислота уксусная, консервант сорбат калия, ароматизатор натуральный Горчица, краситель бета-каротин, подсластитель Сахарин', 
        'Хранить при температуре от 0°C до +14°C', 
        'd5030921-d507-43d9-b234-f316fbcf62be',
        null,
        'Майонез Махеевъ оливковый 50.5%', 
        '770 г', 
        '1.3 г',
        '0.5 г', 
        '50 г',
        '462 ккал',
        null, 
        'Дой-пак', 
        '180 д', 
        '800 мл', 
        '2019-11-13 07:16:07.192982+0000'),
       (4,
        'Концентрат яблочного сока (32%), цельнозерновая пшеничная мука, рисовая мука, негидрогенизированные растительные масла (подсолнечное, кокосовое), молоко сухое обезжиренное, разрыхлители (гидрокарбонат аммония, гидрокарбонат натрия), натуральный экстракт ванили, витамин в1, антиокислитель (токоферол).',
        'Хранить в сухом месте ',
        '8e11bc3f-37d2-44ae-8479-ae0d700c4ec2',
        null,
        'Печенье Fleur Alpine 2 с яблочным соком, с 6 месяцев',
        '150 г',
        '66.8 г',
        '7.2 г',
        '8.3 г',
        '374 ккал',
        'Бельгия',
        'Картонная коробка',
        '450 д',
        null,
        '2019-11-16 14:20:16.653015+0000'),
       (5,
        'Концентрат яблочного сока (32%), цельнозерновая пшеничная мука, рисовая мука, негидрогенизированные растительные масла (подсолнечное, кокосовое), молоко сухое обезжиренное, разрыхлители (гидрокарбонат аммония, гидрокарбонат натрия), натуральный экстракт ванили, витамин в1, антиокислитель (токоферол).',
        'Хранить в сухом месте ',
        '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
        null,
        'Печенье Fleur Alpine 3 с яблочным соком, с 6 месяцев',
        '150 г',
        '66.8 г',
        '7.2 г',
        '8.3 г',
        '374 ккал',
        'Бельгия',
        'Картонная коробка',
        '450 д',
        null,
        '2019-11-16 14:20:16.653015+0000'),
        (6,
        null,
        null,
        '7e11bc3f-9012-5678-1234-ae0d700c4ec4',
        '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
        'sku that should be merged',
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        '2019-11-16 14:20:16.653015+0000');
alter sequence eats_nomenclature.sku_id_seq restart with 50;

insert into eats_nomenclature.pictures (id, url, processed_url)
values  (1, 'https://avatars.mds.yandex.net/get-edadeal/456456456456/123123123/orig', 'https://avatars.mds.yandex.net/get-edadeal/456456456456/123123123/orig'),
        (2, 'https://avatars.mds.yandex.net/get-edadeal/403310/723772bffc977ab631c11e23969fdbed/orig', null),
        (3, 'https://avatars.mds.yandex.net/get-edadeal/2421831/de9f1c29a090887d9b22864ddd51021d/orig', null),
        (4, 'https://avatars.mds.yandex.net/get-edadeal/123123/45645645645645/orig', null),
        (5, 'https://avatars.mds.yandex.net/get-edadeal/472110/c94cd229efdccde56ae2c52a39912b31/orig', null);
alter sequence eats_nomenclature.pictures_id_seq restart with 50;

insert into eats_nomenclature.sku_pictures (sku_id, picture_id, retailer_name)
values  (2, 2, null),
        (1, 3, null),
        (2, 1, 'bystronom'),
        (1, 4, 'miratorg'),
        (3, 5, null);

insert into eats_nomenclature.barcodes (id, unique_key, value)
values  (1, '5412916940854', '5412916940854'),
        (2, '5412916941165', '5412916941165'),
        (3, '4604248002657', '4604248002657');
alter sequence eats_nomenclature.barcodes_id_seq restart with 50;

insert into eats_nomenclature.sku_barcodes (sku_id, barcode_id)
values  (1, 2),
        (2, 1),
        (3, 3);

insert into eats_nomenclature.product_types (id, value_uuid, value)
values  (1, '3df0d4be-644f-5a23-b912-5e6f29fe53c2', 'Печенье детское'),
        (2, '1d6b32ec-430f-5980-8146-f66e2a679d7c', 'Майонез');
alter sequence eats_nomenclature.product_types_id_seq restart with 50;

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values  (1, '40a7405a-84f7-5468-99c5-94d91a2e0100', 'Fleur Alpine'),
        (2, '7116a9b1-5759-531a-a3c5-ec1e9a69c863', 'Махеевъ');
alter sequence eats_nomenclature.product_brands_id_seq restart with 50;

insert into eats_nomenclature.product_processing_types (id, value_uuid, value)
values  (1, '020222a2-e9a9-41ff-a399-9bf15aea8bd2', 'замороженный'),
        (2, '1a8db2fe-03fd-409d-b7df-39c8b76e01eb', 'охлаждённый');
alter sequence eats_nomenclature.product_processing_types_id_seq restart with 50;

insert into eats_nomenclature.sku_attributes (sku_id, product_brand_id, product_type_id, product_processing_type_id)
values  (1, 1, 1, 1),
        (2, 1, 1, 1),
        (3, 2, 2, 2);
