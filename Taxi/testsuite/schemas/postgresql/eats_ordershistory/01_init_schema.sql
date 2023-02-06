CREATE SCHEMA eats_ordershistory;

-- orders data

CREATE TABLE eats_ordershistory.feedbacks(
    order_id TEXT NOT NULL PRIMARY KEY,
    rating INTEGER,
    comment TEXT
);

CREATE TABLE eats_ordershistory.cart_items(
    order_id TEXT NOT NULL,
    place_menu_item_id INTEGER NOT NULL,
    product_id TEXT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,

    PRIMARY KEY (order_id, place_menu_item_id)
);

CREATE TABLE eats_ordershistory.orders(
    order_id TEXT NOT NULL PRIMARY KEY,
    order_source TEXT NOT NULL,

    eats_user_id INTEGER NOT NULL,
    taxi_user_id TEXT,
    yandex_uid TEXT,

    place_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    delivery_location POINT NOT NULL,
    total_amount TEXT NOT NULL,
    is_asap BOOLEAN NOT NULL,
    cancel_reason TEXT,

    created_at TIMESTAMPTZ NOT NULL,
    delivered_at TIMESTAMPTZ
);

CREATE INDEX orders_eats_user_id ON eats_ordershistory.orders(eats_user_id);
CREATE INDEX orders_taxi_user_id ON eats_ordershistory.orders(taxi_user_id);
CREATE INDEX orders_yandex_uid ON eats_ordershistory.orders(yandex_uid);
CREATE INDEX orders_order_source ON eats_ordershistory.orders(order_source);
CREATE INDEX orders_created_at ON eats_ordershistory.orders(created_at);

-- orders meta data

CREATE TABLE eats_ordershistory.users_meta(
    eats_user_id INTEGER NOT NULL PRIMARY KEY,
    orders_count INTEGER NOT NULL
);

CREATE INDEX users_meta_orders_count ON eats_ordershistory.users_meta(orders_count);

-- utility tables

CREATE TABLE eats_ordershistory.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

-- functions for triggers

CREATE FUNCTION inc_user_orders_count()
    RETURNS TRIGGER AS
$$
BEGIN
  INSERT INTO eats_ordershistory.users_meta AS meta (eats_user_id, orders_count)
  VALUES (NEW.eats_user_id, 1)
  ON CONFLICT (eats_user_id) DO UPDATE
  SET orders_count = meta.orders_count + 1;
  RETURN NULL;
END
$$
LANGUAGE plpgsql;

CREATE FUNCTION dec_user_orders_count()
    RETURNS TRIGGER AS
$$
BEGIN
    UPDATE eats_ordershistory.users_meta
    SET orders_count = orders_count - 1
    WHERE eats_user_id = OLD.eats_user_id;
    RETURN NULL;
END
$$
LANGUAGE plpgsql;

CREATE FUNCTION remove_cart_items()
    RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM eats_ordershistory.cart_items
    WHERE order_id = OLD.order_id;
    RETURN NULL;
END
$$
LANGUAGE plpgsql;

CREATE FUNCTION remove_feedback()
    RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM eats_ordershistory.feedbacks
    WHERE order_id = OLD.order_id;
    RETURN NULL;
END
$$
LANGUAGE plpgsql;

CREATE FUNCTION remove_address()
    RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM eats_ordershistory.addresses
    WHERE order_id = OLD.order_id;
    RETURN NULL;
END
$$
LANGUAGE plpgsql;

-- triggers

CREATE TRIGGER add_user_order
AFTER INSERT
ON eats_ordershistory.orders
FOR EACH ROW
EXECUTE PROCEDURE inc_user_orders_count();

CREATE TRIGGER remove_user_order
AFTER DELETE
ON eats_ordershistory.orders
FOR EACH ROW
EXECUTE PROCEDURE dec_user_orders_count();

CREATE TRIGGER remove_order_cart
AFTER DELETE
ON eats_ordershistory.orders
FOR EACH ROW
EXECUTE PROCEDURE remove_cart_items();

CREATE TRIGGER remove_order_feedback
AFTER DELETE
ON eats_ordershistory.orders
FOR EACH ROW
EXECUTE PROCEDURE remove_feedback();

CREATE TRIGGER remove_order_address
AFTER DELETE
ON eats_ordershistory.orders
FOR EACH ROW
EXECUTE PROCEDURE remove_address();

-- types

CREATE TYPE eats_ordershistory.order_v1 AS (
    order_id TEXT,
    order_source TEXT,
    eats_user_id INTEGER,
    taxi_user_id TEXT,
    yandex_uid TEXT,
    place_id INTEGER,
    status TEXT,
    delivery_location POINT,
    total_amount TEXT,
    is_asap BOOLEAN,
    cancel_reason TEXT,
    created_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ
);

CREATE TYPE eats_ordershistory.cart_item_v1 AS (
    order_id TEXT,
    place_menu_item_id INTEGER,
    product_id TEXT,
    name TEXT,
    quantity INTEGER
);

CREATE TYPE eats_ordershistory.feedback_v1 AS (
    order_id TEXT,
    rating INTEGER,
    comment TEXT
);
