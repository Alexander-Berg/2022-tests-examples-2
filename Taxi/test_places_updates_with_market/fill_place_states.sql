INSERT INTO
  fts_indexer.place_state(
    place_id,
    place_slug,
    business,
    enabled,
    market_feed_id,
    market_partner_id,
    market_business_id,
    nomenclature_market_feed_id,
    nomenclature_market_partner_id,
    nomenclature_market_business_id
  )
VALUES (
  1,
  'my_place_slug',
  'shop',
  true,
  100, 101, 102,
  121, 122, 123
),
(
  2,
  'my_place_slug2',
  'shop',
  true,
  200, 201, 202,
  231, 232, 233
),
(
  3,
  'my_place_slug3',
  'shop',
  true,
  300, 301, 302,
  341, 342, 343
);
