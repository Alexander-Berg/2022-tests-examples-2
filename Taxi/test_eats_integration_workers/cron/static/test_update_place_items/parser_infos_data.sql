INSERT INTO eats_integration_workers.parser_infos
(
  place_id,
  brand_id,
  external_id,
  parser_name
)
VALUES
(
  '123',
  'brand_id',
  'external_id',
  'parser_name'
);

INSERT INTO eats_integration_workers.place_items
(
    place_core_id,
    place_item_core_id,
    external_id
)
VALUES
(
  '123',
  'place_item_core_id',
  'external_id'
);
