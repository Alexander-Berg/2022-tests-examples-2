insert into eats_nomenclature.brands (id) values (777);
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, 'lavka_krasina', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);

insert into eats_nomenclature.categories_dictionary(id, name, parent_id)
values (222, 'молочные изделия', null),
       (333, 'сыр', 222),
       (555, 'молочные изделия 5', null),
       (666, 'зелёное молоко', 555);
