START TRANSACTION;

ALTER TABLE eats_ordershistory.orders
    ADD COLUMN ready_to_delivery_at TIMESTAMPTZ,
    ADD COLUMN taken_at TIMESTAMPTZ;

CREATE TYPE eats_ordershistory.order_v5 AS (
   order_id TEXT,
   order_source TEXT,
   eats_user_id INTEGER,
   taxi_user_id TEXT,
   yandex_uid TEXT,
   place_id INTEGER,
   status text,
   delivery_location POINT,
   total_amount TEXT,
   is_asap BOOLEAN,
   cancel_reason TEXT,
   created_at TIMESTAMPTZ,
   delivered_at TIMESTAMPTZ,
   flow_type eats_ordershistory.flow_type_v1,
   order_type eats_ordershistory.order_type_v1,
   original_total_amount TEXT,
   currency TEXT,
   shipping_type eats_ordershistory.shipping_type_v1,
   delivery_type eats_ordershistory.delivery_type_v1,
   last_revision_id TEXT,
   cancelled_at TIMESTAMPTZ,
   ready_to_delivery_at TIMESTAMPTZ,
   taken_at TIMESTAMPTZ
);

COMMIT;
