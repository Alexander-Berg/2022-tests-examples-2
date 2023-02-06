insert into eats_nomenclature.brands (id) values (777);

insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true), (2, '2', true), (3, '3', false);

insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 1), (777, 2), (777, 3);

insert into eats_nomenclature.assortment_traits(brand_id, assortment_name)
values (777, 'assortment_name_1'), (777, 'assortment_name_2');

insert into eats_nomenclature.brand_default_assortments (brand_id, trait_id)
values (777, 1);

insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, null), (2, 2);
