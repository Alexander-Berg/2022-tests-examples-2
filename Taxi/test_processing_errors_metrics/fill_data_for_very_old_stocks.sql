insert into eats_nomenclature.brands (id, slug)
values (1, 'brand1');
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, 'place1', true),
       (2, 'place2', true);

insert into eats_nomenclature.brand_places (brand_id, place_id)
values (1, 1),
       (1, 2);

insert into eats_nomenclature.place_update_statuses
(place_id, enabled_at, price_update_started_at, availability_update_started_at, stock_update_started_at)
values (1, now() - interval '3 hours', now(), now(), now() - interval '25 hours'),
       (2, now() - interval '3 hours', now(), now(), now() - interval '23 hours');
