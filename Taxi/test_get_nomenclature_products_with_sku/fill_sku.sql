insert into eats_nomenclature.sku (id, composition, storage_requirements, uuid, alternate_name, weight, сarbohydrates, proteins, fats, calories, country, package_type, expiration_info, volume, yt_updated_at)
values ( 1,
         'Яблочная паста (концентрированный яблочный сок, концентрированное яблочное  пюре, агент желирующий (пектин), регулятор кислотности (лимонная кислота)),  цельнозерновая пшеничная мука, концентрированный яблочный сок,  негидрогенизированные растительные масла (подсолнечное, кокосовое),  спельтовая мука, яйцо, молоко сухое обезжиренное, рисовая мука, натуральный  экстракт ванили, минералы морских водорослей (кальций, магний), разрыхлители  (карбонат аммония, гидрокарбонат натрия), витамин в1, антиокислитель  (токоферол).',
         'Хранить в сухом месте при температуре не более +25°С, относительной влажности воздуха не более 75%. Для детского питания печенье из открытого пакетика употребить в течение суток. ',
         'f4e3f17d-607c-47a3-9235-3e883b048276',
         'Печенье Fleur Alpine Яблочный мармелад, с 18-ти месяцев',
         '0.15 кг',
         '65 г',
         '6.5 г',
         '11.8 г',
         '388 ккал',
         'Бельгия',
         'Картонная коробка',
         null,
         null,
         '2019-11-16 14:20:16.653015+0000'), (2,
                                'Концентрат яблочного сока (32%), цельнозерновая пшеничная мука, рисовая мука, негидрогенизированные растительные масла (подсолнечное, кокосовое), молоко сухое обезжиренное, разрыхлители (гидрокарбонат аммония, гидрокарбонат натрия), натуральный экстракт ванили, витамин в1, антиокислитель (токоферол).',
                                'Хранить в сухом месте ',
                                '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
                                'Печенье Fleur Alpine с яблочным соком, с 6 месяцев',
                                null,
                                '66.8 г',
                                '7.2 г',
                                '8.3 г',
                                '374 ккал',
                                'Бельгия',
                                'Картонная коробка',
                                null,
                                '100 мл',
                                '2019-11-16 14:20:16.653015+0000'),
        (3, 
        'Масло подсолнечное рафинированное, вода, масло оливковое рафинированное, яичный желток, крахмал, соль, кислота уксусная, консервант сорбат калия, ароматизатор натуральный Горчица, краситель бета-каротин, подсластитель Сахарин', 
        'Хранить при температуре от 0°C до +14°C', 
        'd5030921-d507-43d9-b234-f316fbcf62be',
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
        '2019-11-13 07:16:07.192982+0000');
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
where id = 3;

update eats_nomenclature.products 
set sku_id = 2
where id = 4;

update eats_nomenclature.products 
set sku_id = 3
where id = 6;
