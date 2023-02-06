INSERT INTO
  fts.brand(
    brand_id,
    picture_scale
  )
VALUES (
  1000,
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
  'place_slug',
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
  20,
  200,
  'O_2'
);
