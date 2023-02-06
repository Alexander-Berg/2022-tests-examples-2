-- Brand, place and assortments
insert into eats_nomenclature.brands (id) values (777), (778);
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, '1', true),
       (2, '2', true),
       (3, '3', false),
       (4, '4', true);
insert into eats_nomenclature.brand_places (brand_id, place_id)
values (777, 1),
       (777, 2),
       (778, 3),
       (778, 4);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id)
values (777, 1, 10, 20, 30),
       (777, 2, 40, 50, 60),
       (778, 3, 70, 80, 90);
