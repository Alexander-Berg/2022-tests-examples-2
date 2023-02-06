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
  'my_place_slug',
  true, 'shop',
  100, 101, 102,
  111, 222, 333
)
ON CONFLICT DO NOTHING;
