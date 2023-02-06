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
    ,(2, 'place-2', '2020-06-15T11:00:00Z', 1)
    ,(3, 'place-3', '2020-06-15T11:00:00Z', 1)
;

INSERT INTO eats_products.discount_product (
    place_id, nomenclature_id, updated_at
)
VALUES
     (3, 'existing-product-1', '2020-06-15T11:00:00Z')
    ,(3, 'existing-product-2', '2020-06-15T11:00:00Z')
;
