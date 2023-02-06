CREATE SCHEMA eats_picker_orders;

CREATE TABLE eats_picker_orders.orders (
    id BIGSERIAL PRIMARY KEY,
    eats_id TEXT UNIQUE NOT NULL,
    last_version INTEGER NOT NULL DEFAULT 0,
    picker_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE eats_picker_orders.order_states AS ENUM (
    'new',
    'waiting_dispatch',
    'dispatching',
    'dispatch_failed',
    'assigned',
    'picking',
    'picked_up',
    'paid',
    'packing',
    'handing',
    'cancelled',
    'complete'
);

CREATE TABLE eats_picker_orders.order_statuses (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    last_version INTEGER NOT NULL,
    state eats_picker_orders.order_states NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES eats_picker_orders.orders (id) 
);

CREATE TABLE eats_picker_orders.order_talks (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    talk_id TEXT NOT NULL,
    length INTEGER NOT NULL,
    status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES eats_picker_orders.orders (id)
);

CREATE OR REPLACE FUNCTION eats_picker_orders__remove__order_statuses()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM eats_picker_orders.order_statuses
    WHERE order_id = OLD.id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION eats_picker_orders__remove__order_talks()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM eats_picker_orders.order_talks
    WHERE order_id = OLD.id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER trigger__eats_picker_orders__remove__order_statuses
    BEFORE DELETE ON eats_picker_orders.orders
    FOR EACH ROW
EXECUTE PROCEDURE eats_picker_orders__remove__order_statuses();

CREATE TRIGGER trigger__eats_picker_orders__remove__order_talks
    BEFORE DELETE ON eats_picker_orders.orders
    FOR EACH ROW
EXECUTE PROCEDURE eats_picker_orders__remove__order_talks();
