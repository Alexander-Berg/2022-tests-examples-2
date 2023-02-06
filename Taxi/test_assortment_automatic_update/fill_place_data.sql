insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, '1', true);
insert into eats_nomenclature.places (id, slug, is_enabled) values (2, '2', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 2);
insert into eats_nomenclature.assortment_traits (brand_id, assortment_name) values (777, 'assortment_name');
