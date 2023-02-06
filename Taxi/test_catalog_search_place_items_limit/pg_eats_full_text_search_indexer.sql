INSERT INTO
  fts.brand(
    brand_id,
    picture_scale
  )
VALUES (
  1,
  null
);

INSERT INTO
  fts.place(
    place_id,
    brand_id,
    place_slug,
    enabled
  )
VALUES (
  1,
  1,
  'slug_1',
  true
);

INSERT INTO
  fts.items_mapping(
    place_id,
    core_id,
    core_parent_category_id,
    origin_id
  )
VALUES (
  1,
  1,
  0,
  'O_1'
), (
  1,
  2,
  0,
  'O_2'
);
