START TRANSACTION;

CREATE TYPE eats_ordershistory.cart_item_v4 AS (
   order_id TEXT,
   place_menu_item_id INTEGER,
   name TEXT,
   quantity INTEGER,
   origin_id TEXT,
   catalog_type eats_ordershistory.catalog_type_v1,
   original_quantity INTEGER,
   measure_unit TEXT,
   parent_origin_id TEXT,
   cost_for_customer DECIMAL (13, 2),
   refunded_amount DECIMAL (13, 2),
   weight double precision,
   original_weight double precision,
   standalone_parent_origin_id TEXT
);

COMMIT;
