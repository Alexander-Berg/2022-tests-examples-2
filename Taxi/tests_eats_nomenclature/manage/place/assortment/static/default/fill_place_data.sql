insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug) values (1, 'slug1');
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments(id) values (1);

insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'old_assortment_name'),
       (1, 'new_assortment_name');

insert into eats_nomenclature.place_default_assortments (place_id, trait_id)
values (1, 1);
