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
  'my_place_slug',
  true,
  100, 101, 102,
  'shop'
)
ON CONFLICT DO NOTHING;
