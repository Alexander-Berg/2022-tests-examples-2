START TRANSACTION;

ALTER TABLE eats_ordershistory.cart_items
    ADD CONSTRAINT cart_items_catalog_type_not_null CHECK (catalog_type IS NOT NULL) NOT VALID,
    ADD CONSTRAINT cart_items_origin_id_not_null CHECK (origin_id IS NOT NULL) NOT VALID;

COMMIT;
