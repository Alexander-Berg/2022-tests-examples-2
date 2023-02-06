START TRANSACTION;

ALTER TABLE eats_ordershistory.cart_items
    DROP CONSTRAINT cart_items_pkey,
    ALTER COLUMN place_menu_item_id DROP NOT NULL;

COMMIT;
