insert into eats_nomenclature.places (id, slug, is_enabled) values (2, '2', true), (3, '3', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 2), (777, 3);

insert into eats_nomenclature.brands_for_edadeal (brand_id) values (777);
