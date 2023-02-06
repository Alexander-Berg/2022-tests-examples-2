-- Brand, place and assortments
insert into eats_nomenclature.brands (id, is_enabled, updated_at) 
values (777, true, now()), 
       (778, false, now() - interval '5 minutes'),
       (779, false, now() - interval '1 days');
insert into eats_nomenclature.places (id, slug, is_enabled, updated_at)
values (1, '1', true, now()),
       (2, '2', false, now() - interval '5 minutes'),
       (3, '3', false, now() - interval '1 days');
