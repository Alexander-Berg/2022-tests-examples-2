START TRANSACTION;

ALTER TABLE eats_ordershistory.cart_items
    DROP CONSTRAINT cart_items_origin_id_not_null;

COMMIT;
