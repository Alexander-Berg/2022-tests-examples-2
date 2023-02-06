insert into eats_nomenclature.vendors (id, name, country)
values (1, 'vendor_1', 'country_1'),
       (2, 'vendor_2', 'country_2');

insert into eats_nomenclature.marking_types (id, value)
values (1, 'default'),
       (2, 'energy_drink');

insert into eats_nomenclature.sku (id, uuid, alternate_name, composition, сarbohydrates, proteins, fats, calories,
                                   expiration_info, storage_requirements, country, package_type, weight, volume,
                                   is_alcohol, is_fresh, is_adult, fat_content, milk_type, cultivar, flavour,
                                   meat_type, carcass_part, egg_category, alco_grape_cultivar, alco_flavour, 
                                   alco_aroma, alco_pairing)
values (1, 'a1111111-1111-1111-1111-111111111111', 'Альтернативное имя1', 'Состав1 sku', '11.1', '12.2', '13.3',
        '111.1 ккал', '100 д', 'Хранить в сухом месте при температуре не более +15°С', 'Страна1', 'Упаковка1', '160 г',
        null, true, true, true, '1.1', 'Тип молока1', 'Сорт1', 'Вкус1', 'Тип мяса1', 'Часть тушки1', 'Яйцо1', 'АлкоСорт1', 'АлкоВкус1', 'Аромат1', 'Пейринг1'),
       (2, 'a2222222-2222-2222-2222-222222222222', 'Альтернативное имя2', 'Состав2 sku', '21.1', '22.2', '23.3',
        '222.2 ккал', '200 д', 'Хранить в сухом месте при температуре не более +25°С', 'Страна2', 'Упаковка2', null,
        '270 мл', true, true, true, '2.2', 'Тип молока2', 'Сорт2', 'Вкус2', 'Тип мяса2', 'Часть тушки2', 'Яйцо2', 'АлкоСорт2', 'АлкоВкус2', 'Аромат2', 'Пейринг2');


insert into eats_nomenclature.products (id, public_id, brand_id, origin_id, name, adult, is_catch_weight, is_choosable,
                                        sku_id, description, composition, package_info, vendor_id, measure_unit_id,
                                        measure_value, volume_unit_id, volume_value, marking_type_id)
values (1, 'b1111111-1111-1111-1111-111111111111', 777, 'item_origin_1', 'Товар 1', true, true, true, 1, 'Описание1',
        'Состав1', 'без упаковки1', 1, 1, 150, 1, 120, 1),
       (2, 'b2222222-2222-2222-2222-222222222222', 777, 'item_origin_2', 'Товар 2', true, true, true, 2, 'Описание2',
        'Состав2', 'без упаковки2', 2, 3, 250, 2, 220, 2);


insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, 'c1111111-1111-1111-1111-111111111111', 'Тип 1'),
       (2, 'c2222222-2222-2222-2222-222222222222', 'Тип 2');

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values (1, 'd1111111-1111-1111-1111-111111111111', 'Бренд 1'),
       (2, 'd2222222-2222-2222-2222-222222222222', 'Бренд 2');

insert into eats_nomenclature.product_attributes(product_id, product_type_id, product_brand_id)
values (1, null, null),
       (2, null, null);

insert into eats_nomenclature.sku_attributes(sku_id, product_type_id, product_brand_id)
values (1, null, 1),
       (2, null, 2);

insert into eats_nomenclature.overriden_product_attributes(product_id, product_type_id)
values (1, 1),
       (2, 2);


insert into eats_nomenclature.barcodes(unique_key, value, barcode_weight_encoding_id)
values ('1_1', '11111111', 1),
       ('1_2', '22222222', 2),
       ('2_1', '33333333', 1),
       ('2_2', '44444444', 2);

insert into eats_nomenclature.product_barcodes(product_id, barcode_id)
values (1, 1),
       (1, 2),
       (2, 3),
       (2, 4);

insert into eats_nomenclature.pictures(url, processed_url)
values ('1_1', 'url_1_1'),
       ('1_2', 'url_1_2'),
       ('2_1', 'url_2_1'),
       ('2_2', 'url_2_2');

insert into eats_nomenclature.product_pictures(product_id, picture_id)
values (1, 1),
       (1, 2),
       (2, 3),
       (2, 4);
