INSERT INTO eats_products.brand (
    "brand_id", "slug", "updated_at", "is_enabled"
)
VALUES
    (1, 'brand-1', '2020-06-15T10:00:00Z', TRUE)
;

INSERT INTO eats_products.place (
    "place_id", "slug", "updated_at", "brand_id"
)
VALUES
     (1, 'place-1', '2020-06-15T11:00:00Z', 1)
;
