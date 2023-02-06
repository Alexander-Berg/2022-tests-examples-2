INSERT INTO eats_products.brand(brand_id, slug, is_enabled)
VALUES (1, 'brand_slug1', True);

INSERT INTO eats_products.place(place_id, slug, brand_id)
VALUES (1, 'slug1', 1), (2, 'slug2', 1), (3, 'slug3', 1);

INSERT INTO eats_products.market_feed_places(place_id)
VALUES (1), (2), (3);
