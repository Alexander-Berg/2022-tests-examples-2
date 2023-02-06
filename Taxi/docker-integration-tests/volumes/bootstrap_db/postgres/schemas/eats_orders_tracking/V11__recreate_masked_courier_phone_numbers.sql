/* V11 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

-- При обновлении базы отключим маскировку телефонов курьеров.
-- Поэтому можно просто пересоздать таблицу.
DROP TABLE eats_orders_tracking.masked_courier_phone_numbers;

CREATE TABLE eats_orders_tracking.masked_courier_phone_numbers
(
    order_nr TEXT NOT NULL,
    phone_number TEXT,
    extension TEXT,
    ttl TIMESTAMPTZ,
    error_count SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

CREATE INDEX IF NOT EXISTS masked_courier_phone_numbers_order_nr_ttl_error_count_idx
    ON eats_orders_tracking.masked_courier_phone_numbers (order_nr, ttl, error_count);

CREATE INDEX IF NOT EXISTS masked_courier_phone_numbers_updated_at_idx
    ON eats_orders_tracking.masked_courier_phone_numbers (updated_at);

COMMIT;
