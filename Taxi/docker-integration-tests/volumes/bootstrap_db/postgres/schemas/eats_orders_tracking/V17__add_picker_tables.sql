/* V17 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

-- таблица заказов из пикерки
CREATE TABLE IF NOT EXISTS eats_orders_tracking.picker_orders
(
    order_nr TEXT NOT NULL,
    payload JSONB NOT NULL, -- пэйлоад с кэшированными данными по заказу
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

CREATE INDEX IF NOT EXISTS picker_orders_created_at_idx
    ON eats_orders_tracking.picker_orders (created_at);
CREATE INDEX IF NOT EXISTS picker_orders_updated_at_idx
    ON eats_orders_tracking.picker_orders (updated_at);

-- таблица телефонов сборщиков из пикерки
CREATE TABLE IF NOT EXISTS eats_orders_tracking.picker_phones
(
    picker_id TEXT NOT NULL,
    personal_phone_id TEXT NOT NULL,
    extension TEXT,
    ttl TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (picker_id)
);

CREATE INDEX IF NOT EXISTS picker_phones_created_at_idx
    ON eats_orders_tracking.picker_phones (created_at);
CREATE INDEX IF NOT EXISTS picker_phones_updated_at_idx
    ON eats_orders_tracking.picker_phones (updated_at);

COMMIT;
