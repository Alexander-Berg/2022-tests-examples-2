insert into
  eats_retail_market_integration.brands (id, slug)
values
  ('1', 'brand_1'),
  ('2', 'brand_2'),
  ('3', 'brand_3');

insert into
  eats_retail_market_integration.places (id, slug, brand_id)
values
  ('1', 'place_1', '1'),
  ('2', 'place_2', '2'),
  ('3', 'place_3', '3');

insert into
  eats_retail_market_integration.market_brand_places (
    brand_id,
    place_id,
    business_id,
    partner_id,
    feed_id
  )
values
('1', '1', 1, 1, 1),
('2', '2', 2, 2, 2);
