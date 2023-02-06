INSERT INTO fts.brand(brand_id, picture_scale)
VALUES (1, null);

INSERT INTO fts.place(place_id, brand_id, place_slug, enabled)
VALUES
  (1, 1, 'slug_1', true),
  (2, 1, 'slug_2', true),
  (3, 1, 'slug_3', true),
  (4, 1, 'slug_4', true),
  (5, 1, 'slug_5', true),
  (6, 1, 'slug_6', true),
  (7, 1, 'slug_7', true);

INSERT INTO fts.items_mapping(
    place_id,
    core_id,
    core_parent_category_id,
    origin_id
)
VALUES
  (1, 1, 0, 'O_1'),
  (1, 3, 0, 'O_3'),
  (1, 4, 0, 'O_4'),
  (1, 5, 0, 'O_5'),
  (2, 1, 0, 'O_1'),
  (2, 2, 0, 'O_2'),
  (2, 3, 0, 'O_3'),
  (2, 4, 0, 'O_4'),
  (3, 3, 0, 'O_3'),
  (3, 6, 0, 'O_6'),
  (3, 7, 0, 'O_7'),
  (3, 8, 0, 'O_8'),
  (4, 9, 0, 'O_9'),
  (5, 1, 0, 'O_1'),
  (5, 2, 0, 'O_2'),
  (5, 10, 0, 'O_10'),
  (6, 2, 0, 'O_2'),
  (6, 3, 0, 'O_3'),
  (6, 10, 0, 'O_10'),
  (7, 11, 0, 'O_11');
