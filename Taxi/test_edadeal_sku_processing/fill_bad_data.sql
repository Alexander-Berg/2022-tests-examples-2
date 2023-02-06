insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.edadeal_export_tasks
    (id, brand_id, s3_export_path, export_retailer_name, exported_at, processed)
values (default, 1, 'unknown', 'unknown', now(),
        true);

insert into eats_nomenclature.edadeal_sku_import_tasks
    (id, edadeal_export_task_id, yt_path, status, details)
values (default, 1, '//unknown', 'new', '');
