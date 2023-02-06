insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, 'lavka_krasina', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);

insert into eats_nomenclature.categories_dictionary(id, name)
values (111, 'category_1'),
       (222, 'category_2');
