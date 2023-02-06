INSERT INTO eats_products.brand (brand_id, slug, is_enabled)
VALUES (5, 'brand_5_slug', TRUE);

INSERT INTO eats_products.place (place_id, slug, brand_id, is_enabled)
VALUES (1, 'place1', 5, TRUE),
       (2, 'place2', 5, TRUE),
       (3, 'place3', 5, FALSE),
       (4, 'place4', 5, FALSE);
