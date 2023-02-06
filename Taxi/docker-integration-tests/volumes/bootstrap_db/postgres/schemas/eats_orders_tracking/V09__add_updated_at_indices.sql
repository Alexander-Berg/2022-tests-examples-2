/* V9 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

ALTER TABLE eats_orders_tracking.masked_courier_phone_numbers
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE eats_orders_tracking.masked_courier_phone_numbers
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS orders_updated_at_idx ON eats_orders_tracking.orders (updated_at);

CREATE INDEX IF NOT EXISTS couriers_updated_at_idx ON eats_orders_tracking.couriers (updated_at);

CREATE INDEX IF NOT EXISTS couriers_dynamic_data_updated_at_idx ON eats_orders_tracking.couriers_dynamic_data (updated_at);

CREATE INDEX IF NOT EXISTS places_updated_at_idx ON eats_orders_tracking.places (updated_at);

CREATE INDEX IF NOT EXISTS eater_to_place_masking_states_updated_at_idx ON eats_orders_tracking.eater_to_place_masking_states (updated_at);

CREATE INDEX IF NOT EXISTS masked_courier_phone_numbers_updated_at_idx ON eats_orders_tracking.masked_courier_phone_numbers (updated_at);

COMMIT;
