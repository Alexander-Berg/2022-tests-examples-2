INSERT INTO
  fts_indexer.place_state(
    place_id,
    place_slug,
    enabled,
    business
  )
VALUES (
  1,
  'place_slug',
  true,
  'shop'
),
(
  2,
  'place_slug_2',
  false,
  null -- проверяем что business может оказаться пустым
);
