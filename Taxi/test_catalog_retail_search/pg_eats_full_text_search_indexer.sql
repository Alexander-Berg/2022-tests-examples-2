INSERT INTO fts.brand(brand_id, picture_scale)
VALUES (1, null);

INSERT INTO fts.place(place_id, brand_id, place_slug, enabled)
VALUES
  (1, 1, 'slug_1', true),
  (2, 1, 'slug_2', true),
  (3, 1, 'slug_3', true);

INSERT INTO fts.items_mapping(
    place_id,
    core_id,
    core_parent_category_id,
    origin_id
)
VALUES
  (1, 1, 1, 'origin_id_1'),
  (1, 2, 1, 'origin_id_2'),
  (2, 3, 1, 'origin_id_3'),
  (2, 4, 1, 'origin_id_4'),
  (2, 5, 1, 'origin_id_5'),
  (2, 6, 1, 'origin_id_6');
