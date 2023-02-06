CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
    idx_cart_items_order_catalog_type_origin_parent_standalone_ids
    ON eats_ordershistory.cart_items (
        order_id,
        catalog_type,
        COALESCE(origin_id, ''),
        COALESCE(parent_origin_id, ''),
        COALESCE(standalone_parent_origin_id, '')
    );

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
    cart_items_order_id_catalog_type_origin_id
    ON eats_ordershistory.cart_items (order_id, catalog_type, origin_id)
    WHERE origin_id IS NOT NULL;
