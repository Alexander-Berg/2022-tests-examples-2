insert into eats_retail_business_alerts.brands(id, slug, name, is_enabled)
values (1, 'slug', 'name', true);

insert into eats_retail_business_alerts.regions(id, slug, name, is_enabled)
values (1, 'slug', 'name', true);

insert into eats_retail_business_alerts.places(id, slug, name, is_enabled, brand_id, region_id)
values (1, 'slug', 'name', true, 1, 1);
