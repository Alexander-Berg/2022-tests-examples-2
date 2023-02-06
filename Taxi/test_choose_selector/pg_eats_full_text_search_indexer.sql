INSERT INTO fts.brand(brand_id, picture_scale)
VALUES (1, null);

INSERT INTO fts.place(place_id, brand_id, place_slug, enabled)
VALUES
  (1, 1, 'slug_1', true),
  (2, 1, 'slug_2', true);

INSERT INTO fts.items_mapping(
    place_id,
    core_id,
    core_parent_category_id,
    origin_id
)
VALUES
  (1, 1, 1, 'N_1'),
  (2, 2, 2, 'N_2');
