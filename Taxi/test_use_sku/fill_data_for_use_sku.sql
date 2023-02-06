insert into eats_nomenclature.sku (id, uuid, alternate_name, composition, сarbohydrates, proteins, fats, calories,
                                   expiration_info, storage_requirements, country, package_type, weight, volume,
                                   is_alcohol, is_fresh, is_adult)
values (1, 'a1111111-1111-1111-1111-111111111111', 'Альтернативное имя1', 'Состав1 sku', '11.1', '12.2', '13.3',
        '111.1 ккал', '100 д', 'Хранить в сухом месте при температуре не более +15°С', 'Страна1', 'Упаковка1', '160 г',
        null, true, true, true);


insert into eats_nomenclature.products (id, public_id, brand_id, origin_id, name, adult, is_catch_weight, is_choosable,
                                        sku_id, description, composition, package_info, measure_unit_id,
                                        measure_value, volume_unit_id, volume_value)
values (1, 'b1111111-1111-1111-1111-111111111111', 777, 'item_origin_1', 'Товар 1', true, false, true, 1, 'Описание1',
        'Состав1', 'без упаковки1', 1, 150, 1, 120);


insert into eats_nomenclature.product_types (id, value_uuid, value)
values (1, 'c1111111-1111-1111-1111-111111111111', 'Тип 1');

insert into eats_nomenclature.product_brands (id, value_uuid, value)
values (1, 'd1111111-1111-1111-1111-111111111111', 'Бренд 1');

insert into eats_nomenclature.product_attributes(product_id, product_type_id, product_brand_id)
values (1, null, null);

insert into eats_nomenclature.sku_attributes(sku_id, product_type_id, product_brand_id)
values (1, null, 1);

insert into eats_nomenclature.overriden_product_attributes(product_id, product_type_id)
values (1, 1);

insert into eats_nomenclature.pictures(url, processed_url)
values ('url_1', 'url_1'),
       ('url_2', 'url_2'),
       ('sku_url_1', 'sku_url_1');

insert into eats_nomenclature.product_pictures(product_id, picture_id)
values (1, 1),
       (1, 2);

insert into eats_nomenclature.sku_pictures(sku_id, picture_id)
values (1, 3);
