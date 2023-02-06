INSERT INTO
  fts_indexer.place_state(
    place_id,
    place_slug,
    enabled,
    business,
    market_feed_id,
    market_partner_id,
    market_business_id,
    nomenclature_market_feed_id,
    nomenclature_market_partner_id,
    nomenclature_market_business_id
  )
VALUES (
  1,
  'my_place_slug_1',
  true, 'shop',
  100, 101, 102,
  111, 101, 333
), (
  2,
  'my_place_slug_2',
  true, 'shop',
  200, 201, 202,
  444, 201, 666
), (
  3,
  'my_place_slug_3',
  true, 'restaurant',
  300, 301, 302,
  NULL, 301, NULL
), (
  4,
  'my_place_slug_4',
  true, 'restaurant',
  400, 401, 402,
  NULL, 401, NULL
)
ON CONFLICT DO NOTHING;
