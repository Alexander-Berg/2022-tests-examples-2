insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'),
       ('vendor_2', 'country_2'),
       ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum,
                                        measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('РН113367', 'def', 2, 1, 'item_2', 0.0, null, null,
        false, false, true, 1, '22222222222222222222222222222222'),
       ('РН117357', 'def', 2, 1, 'item_2', 0.0, null, null,
        false, false, true, 1, '33333333333333333333333333333333');

insert into eats_nomenclature.edadeal_export_tasks
(id, brand_id, s3_export_path, export_retailer_name, exported_at, processed)
values (default, 1, 'vkusvill/2019-12-07', 'vkusvill', now(),
        true);

insert into eats_nomenclature.edadeal_tag_import_tasks
    (id, edadeal_export_task_id, yt_path, status, details)
values (default, 1, '//edadeal_yt/proccessed/vkusvill/2019-12-07', 'new', '');
