CREATE SCHEMA cargo_orders;

-- cargo_orders.orders
CREATE TYPE cargo_orders.order_commit_state AS ENUM (
       'draft',
       'done',
       'failed'
);

CREATE TABLE cargo_orders.orders (
    order_id UUID NOT NULL PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- cargo_orders.orders_performers
CREATE TABLE cargo_orders.orders_performers (
    order_id UUID NOT NULL PRIMARY KEY REFERENCES cargo_orders.orders (order_id),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE cargo_orders.orders_client_robocalls (
    order_id UUID NOT NULL,
    point_id TEXT NOT NULL,
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(order_id, point_id)
 );

CREATE TABLE cargo_orders.orders_client_robocall_attempts (
    order_id UUID NOT NULL,
    point_id TEXT NOT NULL,
    attempt_id INT NOT NULL,
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(order_id, point_id, attempt_id)
 );

CREATE INDEX idx__orders_performer__updated_ts ON cargo_orders.orders_performers(updated_ts);

CREATE INDEX idx__orders_client_robocalls__updated_ts ON cargo_orders.orders_client_robocalls(updated_ts);

CREATE INDEX idx__orders_client_robocall_attempts__updated_ts ON cargo_orders.orders_client_robocall_attempts(updated_ts);

-- archiving function
CREATE OR REPLACE FUNCTION cargo_orders__update_ts()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE cargo_orders.orders
    SET updated = NOW()
    WHERE order_id = NEW.order_id;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

--- cargo_orders.orders_performers archiving triggers
CREATE TRIGGER trigger__orders_performers__cargo_orders_update_ts
    AFTER INSERT OR UPDATE ON cargo_orders.orders_performers
    FOR EACH ROW
EXECUTE PROCEDURE cargo_orders__update_ts();

CREATE OR REPLACE FUNCTION cargo_orders__remove__orders_performers()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM cargo_orders.orders_performers
    WHERE order_id = OLD.order_id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER trigger__cargo_orders__remove__orders_performers
    BEFORE DELETE ON cargo_orders.orders
    FOR EACH ROW
EXECUTE PROCEDURE cargo_orders__remove__orders_performers();
