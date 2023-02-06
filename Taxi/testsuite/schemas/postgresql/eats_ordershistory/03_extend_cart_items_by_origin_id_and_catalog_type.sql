START TRANSACTION;

CREATE TYPE eats_ordershistory.catalog_type_v1 AS ENUM (
    'core_catalog',
    'lavka_catalog',
    'eats_nomenclature',
    'eats_restaurant_nomenclature'
    );

ALTER TABLE eats_ordershistory.cart_items
    ADD COLUMN origin_id TEXT,
    ADD COLUMN catalog_type eats_ordershistory.catalog_type_v1;

CREATE TYPE eats_ordershistory.cart_item_v2 AS (
    order_id TEXT,
    place_menu_item_id INTEGER,
    product_id TEXT,
    name TEXT,
    quantity INTEGER,
    origin_id TEXT,
    catalog_type eats_ordershistory.catalog_type_v1
    );

COMMIT;
