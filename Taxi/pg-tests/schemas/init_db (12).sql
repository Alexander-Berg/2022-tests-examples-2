CREATE SCHEMA cart;

CREATE TABLE cart.cart_items
(
    cart_id    UUID,
    item_id    TEXT,
    updated    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id, item_id)
);

CREATE TABLE cart.carts
(
    cart_id      UUID PRIMARY KEY,
    updated      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_out BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE cart.checkout_data
(
    cart_id      UUID PRIMARY KEY,
    updated      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION remove_items()
  RETURNS trigger AS
$$
BEGIN
DELETE FROM cart.cart_items items
WHERE items.cart_id = OLD.cart_id;
return NULL;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER cart_delete_cleanup
AFTER DELETE
ON cart.carts
FOR EACH ROW
EXECUTE PROCEDURE remove_items();
