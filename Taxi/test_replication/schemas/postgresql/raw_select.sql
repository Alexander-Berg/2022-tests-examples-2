CREATE SCHEMA cart;

CREATE TABLE cart.cart_items
(
    cart_id    TEXT,
    item_id    TEXT,
    updated    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id, item_id)
);

CREATE TABLE cart.carts
(
    cart_id      TEXT PRIMARY KEY,
    updated      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_out BOOLEAN NOT NULL DEFAULT FALSE
);
