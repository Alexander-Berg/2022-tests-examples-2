insert into eats_nomenclature.brands (id)
values (1);

insert into eats_nomenclature.edadeal_export_tasks
    (id, brand_id, s3_export_path, export_retailer_name, exported_at)
values (default, 1, 'bystronom/2019-12-06', 'bystronom', now());
