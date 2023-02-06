INSERT INTO
  fts_indexer.place_state(
    place_id,
    place_slug,
    enabled,
    market_feed_id,
    market_partner_id,
    market_business_id,
    business
  )
VALUES (
  1,
  'my_place_slug_1',
  true, 100, 101, 102,
  'shop'
), (
  2,
  'my_place_slug_2',
  true, 200, 201, 202,
  'shop'
), (
  3,
  'my_place_slug_3',
  true, 300, 301, 302,
  'shop'
), (
  4,
  'my_place_slug_4',
  true, 400, 401, 402,
  'shop'
)
ON CONFLICT DO NOTHING;
