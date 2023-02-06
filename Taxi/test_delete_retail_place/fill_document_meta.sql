INSERT INTO
  fts_indexer.place_state(
    place_id,
    place_slug,
    enabled
) VALUES (
  1,
  'place_slug',
  false
);


INSERT INTO
  fts_indexer.retail_document_meta(
    prefix,
    place_slug,
    url,
    hash
) VALUES (
  1,
  'place_slug',
  '/place_slug/categories/category_id_1',
  'hash1'
), (
  1,
  'place_slug',
  '/place_slug/categories/category_id_2',
  'hash2'
), (
  2,
  'place_slug',
  '/1/items/item_id_1',
  'hash3'
),  (
  2,
  'place_slug',
  '/1/items/item_id_2',
  'hash4'
);
