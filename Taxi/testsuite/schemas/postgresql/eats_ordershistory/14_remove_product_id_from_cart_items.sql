START TRANSACTION;

ALTER TABLE eats_ordershistory.cart_items
    DROP COLUMN product_id;

COMMIT;
