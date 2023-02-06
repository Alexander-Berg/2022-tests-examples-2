INSERT INTO
  fts_indexer.document_meta(
    prefix,
    place_slug,
    url,
    hash
) VALUES (
  1,
  'place_slug',
  '/place_slug/categories/1',
  'hash1'
), (
  1,
  'place_slug',
  '/place_slug/categories/2',
  'hash2'
), (
  1,
  'place_slug',
  '/place_slug/items/public_item_1',
  'hash3'
), (
  1,
  'place_slug',
  '/place_slug/items/public_item_2',
  'hash4'
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
  '/place_slug/categories/1',
  'hash1'
), (
  1,
  'place_slug',
  '/place_slug/categories/2',
  'hash2'
), (
  2,
  'place_slug',
  '/1/items/public_item_1',
  'hash3'
),  (
  2,
  'place_slug',
  '/1/items/public_item_2',
  'hash3'
);
