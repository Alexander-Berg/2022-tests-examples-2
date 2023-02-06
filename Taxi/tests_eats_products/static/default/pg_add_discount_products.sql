INSERT INTO eats_products.discount_product (
    place_id, nomenclature_id, updated_at
)
VALUES
     (1, 'item_id_1', '2020-06-15T11:00:00Z')
    ,(1, 'item_id_2', '2020-06-15T11:00:00Z')
    ,(1, 'item_id_3', '2020-06-15T11:00:00Z')
    ,(1, 'item_id_4', '2020-06-15T11:00:00Z')
    ,(1, 'item_id_5', '2020-06-15T11:00:00Z')
    ,(1, 'item_id_7', '2020-06-15T11:00:00Z')
;


INSERT INTO eats_products.place_products (
    place_id, brand_id, origin_id, core_id, public_id, updated_at
)
VALUES (1, 1, 'item_id_1', 1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', now())
     , (1, 1, 'item_id_2', 2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', now())
     , (1, 1, 'item_id_3', 3, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', now())
     , (1, 1, 'item_id_7', 7, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', now())
;
