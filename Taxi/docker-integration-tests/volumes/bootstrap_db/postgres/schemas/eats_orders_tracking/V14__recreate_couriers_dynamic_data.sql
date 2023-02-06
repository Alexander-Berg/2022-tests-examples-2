/* V14 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

-- Пока сервис не используется случайными клиентами.
-- Поэтому можно просто пересоздать таблицу.
DROP TABLE IF EXISTS eats_orders_tracking.couriers_dynamic_data;

CREATE TABLE IF NOT EXISTS eats_orders_tracking.couriers_dynamic_data
(
    order_nr TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

CREATE INDEX IF NOT EXISTS couriers_dynamic_data_updated_at_idx
    ON eats_orders_tracking.couriers_dynamic_data (updated_at);

COMMIT;
