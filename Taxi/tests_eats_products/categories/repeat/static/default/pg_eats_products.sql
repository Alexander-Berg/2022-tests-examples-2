INSERT INTO eats_products.brand (
    "brand_id", "slug", "picture_scale", "updated_at", "is_enabled"
)
VALUES
    (1, 'brand1', 'aspect_fit', '2020-06-15T10:00:00Z', True)
;

INSERT INTO eats_products.place (
    "place_id", "slug", "updated_at", "brand_id", "is_enabled"
)
VALUES
    (1, 'slug', '2020-06-15T11:00:00Z', 1, true)
;

INSERT INTO eats_products.place_update_statuses (
    "place_id", "enabled_at"
)
VALUES
    (1, '2020-06-15T11:00:00Z')
;
