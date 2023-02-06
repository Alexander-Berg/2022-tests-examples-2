INSERT INTO
  fts.brand(
    brand_id,
    picture_scale
  )
VALUES (
  1000,
  'aspect_fit'
), (
  2000,
  'aspect_fit'
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
  1000,
  'my_place_slug_1',
  true
), (
  2,
  1000,
  'my_place_slug_2',
  true
), (
  3,
  2000,
  'my_place_slug_3',
  true
), (
  4,
  2000,
  'my_place_slug_4',
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
  10,
  100,
  'N_10'
), (
  2,
  20,
  200,
  'N_20'
);
