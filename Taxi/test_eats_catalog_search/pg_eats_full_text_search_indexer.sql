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
), (
  2,
  1,
  'slug_2',
  true
), (
  3,
  1,
  'slug_3',
  true
), (
  4,
  1,
  'slug_4',
  true
), (
  5,
  1,
  'slug_5',
  true
), (
  6,
  1,
  'slug_6',
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
  2,
  1,
  0,
  'O_1'
), (
  3,
  2,
  0,
  'O_2'
), (
  6,
  3,
  0,
  'O_3'
);
