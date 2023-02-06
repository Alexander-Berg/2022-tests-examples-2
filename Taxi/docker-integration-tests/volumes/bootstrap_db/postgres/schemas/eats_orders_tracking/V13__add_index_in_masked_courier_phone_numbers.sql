/* V13 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE INDEX IF NOT EXISTS masked_courier_phone_numbers_created_at_idx
    ON eats_orders_tracking.masked_courier_phone_numbers (created_at);

COMMIT;
