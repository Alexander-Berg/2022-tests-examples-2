CREATE SCHEMA cargo_c2c;

--- cargo_c2c.clients_orders table
CREATE TYPE cargo_c2c.handlers__order_provider_id AS ENUM (
    'cargo-claims',
    'cargo-c2c'
);

CREATE TABLE IF NOT EXISTS cargo_c2c.clients_orders (
    phone_pd_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    order_provider_id cargo_c2c.handlers__order_provider_id NOT NULL,

    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    terminated_at TIMESTAMPTZ,

    PRIMARY KEY(phone_pd_id, order_id, order_provider_id)
);

CREATE OR REPLACE FUNCTION clients_orders_update_ts()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE cargo_c2c.clients_orders
    SET updated_ts = NOW()
    WHERE order_id = NEW.order_id;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

--- cargo_c2c.clients_feedbacks table
CREATE TABLE IF NOT EXISTS cargo_c2c.clients_feedbacks (
    phone_pd_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    order_provider_id cargo_c2c.handlers__order_provider_id NOT NULL,
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (phone_pd_id, order_id, order_provider_id),
    FOREIGN KEY (phone_pd_id, order_id, order_provider_id)
        REFERENCES cargo_c2c.clients_orders (phone_pd_id, order_id, order_provider_id)
);

--- cargo_c2c.clients_feedbacks triggers
CREATE TRIGGER trigger_clients_orders_update_ts_feedbacks
    AFTER INSERT OR UPDATE ON cargo_c2c.clients_feedbacks
    FOR EACH ROW
EXECUTE PROCEDURE clients_orders_update_ts();


CREATE OR REPLACE FUNCTION clients_orders_remove_clients_feedbacks()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM cargo_c2c.clients_feedbacks
    WHERE (
        phone_pd_id = OLD.phone_pd_id AND
        order_id = OLD.order_id AND
        order_provider_id = OLD.order_provider_id
    );
    RETURN OLD;
END
$$
LANGUAGE plpgsql;


CREATE TRIGGER trigger_clients_orders_remove_clients_feedbacks
    BEFORE DELETE ON cargo_c2c.clients_orders
    FOR EACH ROW
EXECUTE PROCEDURE clients_orders_remove_clients_feedbacks();


--- cargo_c2c.orders table
CREATE TABLE IF NOT EXISTS cargo_c2c.orders (
    order_id TEXT PRIMARY KEY,
    offer_id TEXT NOT NULL,
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

--- cargo_c2c.orders triggers
CREATE TRIGGER trigger_clients_orders_update_ts_orders
    AFTER INSERT OR UPDATE ON cargo_c2c.orders
    FOR EACH ROW
EXECUTE PROCEDURE clients_orders_update_ts();

CREATE OR REPLACE FUNCTION clients_orders_remove_orders()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM cargo_c2c.orders
    WHERE order_id = OLD.order_id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER trigger_clients_orders_remove_orders
    BEFORE DELETE ON cargo_c2c.clients_orders
    FOR EACH ROW
    WHEN (OLD.order_provider_id = 'cargo-c2c'::cargo_c2c.handlers__order_provider_id)
EXECUTE PROCEDURE clients_orders_remove_orders();

--- cargo_c2c.orderhistory_deleted_clients_orders table
CREATE TABLE IF NOT EXISTS cargo_c2c.orderhistory_deleted_clients_orders (
    phone_pd_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    order_provider_id cargo_c2c.handlers__order_provider_id NOT NULL,

    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY(phone_pd_id, order_id, order_provider_id)
);

--- cargo_c2c.offers table
CREATE TABLE IF NOT EXISTS cargo_c2c.offers (
    offer_id TEXT PRIMARY KEY,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

--- cargo_c2c.offers triggers
CREATE OR REPLACE FUNCTION offers_update_ts()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE cargo_c2c.offers
    SET updated_ts = NOW()
    WHERE offer_id = NEW.offer_id;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trigger_offers_update_ts_orders
    AFTER INSERT ON cargo_c2c.orders
    FOR EACH ROW
EXECUTE PROCEDURE offers_update_ts();

CREATE OR REPLACE FUNCTION orders_remove_offers()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM cargo_c2c.offers
    WHERE offer_id = OLD.offer_id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;
 
CREATE TRIGGER trigger_orders_remove_offers
    BEFORE DELETE ON cargo_c2c.orders
    FOR EACH ROW
EXECUTE PROCEDURE orders_remove_offers();

--- cargo_c2c.offers_v2 table
CREATE TABLE IF NOT EXISTS cargo_c2c.offers_v2 (
    offer_id TEXT PRIMARY KEY,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

--- cargo_c2c.offers_v2 triggers
CREATE OR REPLACE FUNCTION offers_v2_update_ts()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE cargo_c2c.offers_v2
    SET updated_ts = NOW()
    WHERE offer_id = NEW.offer_id;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trigger_offers_v2_update_ts_orders
    AFTER INSERT ON cargo_c2c.orders
    FOR EACH ROW
EXECUTE PROCEDURE offers_v2_update_ts();

CREATE OR REPLACE FUNCTION orders_remove_offers_v2()
  RETURNS TRIGGER AS
$$
BEGIN
    DELETE FROM cargo_c2c.offers_v2
    WHERE offer_id = OLD.offer_id;
    RETURN OLD;
END
$$
LANGUAGE plpgsql;
 
CREATE TRIGGER trigger_orders_remove_offers_v2
    BEFORE DELETE ON cargo_c2c.orders
    FOR EACH ROW
EXECUTE PROCEDURE orders_remove_offers_v2();

--- cargo_c2c.lp_status_history
CREATE TABLE IF NOT EXISTS cargo_c2c.lp_status_history(
    order_id TEXT PRIMARY KEY,
    last_status_id INT,
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
