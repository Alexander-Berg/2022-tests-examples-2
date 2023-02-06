CREATE INDEX CONCURRENTLY IF NOT EXISTS cart_items_order_id
    ON eats_ordershistory.cart_items (order_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS cart_items_origin_id
    ON eats_ordershistory.cart_items (origin_id);

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
    cart_items_order_id_catalog_type_origin_id
    ON eats_ordershistory.cart_items (order_id, catalog_type, origin_id);
