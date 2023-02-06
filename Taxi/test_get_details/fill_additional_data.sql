INSERT INTO eats_products.place (
    "place_id", "slug", "updated_at", "brand_id", "is_enabled"
)
VALUES
    (2, 'slug2', '2020-06-15T11:00:00Z', 1, true);

INSERT INTO eats_products.place_products(
    place_id, brand_id, origin_id, core_id, public_id
) VALUES
    (1, 1, 'origin_id_101', 101, 'public_101'),
    (1, 1, 'origin_id_102', 102, 'public_102'),
    (1, 1, 'origin_id_103', 103, 'public_103'),
    (1, 1, 'origin_id_104', 104, 'public_104'),
    (2, 1, 'origin_id_201', 201, 'public_201'),
    (2, 1, 'origin_id_202', 202, 'public_202');
