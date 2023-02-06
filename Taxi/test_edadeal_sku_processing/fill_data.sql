insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1'), ('vendor_2', 'country_2'), ('vendor_3', 'country_3');

insert into eats_nomenclature.products (origin_id, description, shipping_type_id, vendor_id, name, quantum, measure_unit_id, measure_value, adult, is_catch_weight, is_choosable, brand_id, public_id)
values ('item_origin_1', 'abc', 1, 1, 'item_1', 0.2, 1, 1000, false, false, true, 1, '11111111111111111111111111111111'),
       ('item_origin_2', 'def', 2, 1, 'Сок U! Ананасовый', 1.0, 1, 1000, true, true, true, 1, '22222222-2222-2222-2222-222222222222'),
       ('item_origin_3', 'ghi', 2, 2, 'Печенье детское Органик Яблочный мармелад 18 мес. Alpine', 1.0, null, null, false, true, true, 1, '33333333-3333-3333-3333-333333333333'),
       ('item_origin_4', 'jkl', 3, 2, 'Печенье Fleur Alpine с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444444'),
       ('item_origin_5', 'mno', 3, 3, 'item_5', 0.5, 1, 300, true, true, true, 1, '55555555555555555555555555555555'),
       ('item_origin_6', 'jkl', 3, 2, 'Майонез', 1.0, 1, 50, true, true, false, 1, '66666666-6666-6666-6666-666666666666'),
       ('item_origin_7', 'jkl', 3, 2, 'Печенье Fleur Alpine 2 с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444445'),
       ('item_origin_8', 'jkl', 3, 2, 'Печенье Fleur Alpine 3 с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444446'),
       ('item_origin_9', 'jkl', 3, 2, 'Печенье Fleur Alpine 4 с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444447'),
       ('item_origin_10', 'jkl', 3, 2, 'Печенье Fleur Alpine 5 с яблочным соком, с 6 месяцев, 150 г', 1.0, 1, 50, true, true, false, 1, '44444444-4444-4444-4444-444444444448');

insert into eats_nomenclature.edadeal_export_tasks
    (id, brand_id, s3_export_path, export_retailer_name, exported_at, processed)
values (default, 1, 'bystronom/2019-12-06', 'bystronom', now(),
        true);

insert into eats_nomenclature.edadeal_sku_import_tasks
    (id, edadeal_export_task_id, yt_path, status, details)
values (default, 1, '//edadeal_yt/proccessed/bystronom/2019-12-06', 'new', '');
