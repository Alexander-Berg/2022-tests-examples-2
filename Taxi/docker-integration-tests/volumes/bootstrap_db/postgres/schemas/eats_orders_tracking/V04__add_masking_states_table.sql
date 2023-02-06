/* V2 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE TYPE eats_orders_tracking.masking_state AS ENUM('success', 'disabled_for_region', 'disabled_globally', 'place_has_no_phone',
'has_extension', 'masking_error', 'unrecognized_error');

CREATE TABLE IF NOT EXISTS eats_orders_tracking.eater_to_place_masking_states
(
    order_nr TEXT NOT NULL,
    state eats_orders_tracking.masking_state NOT NULL,
    proxy_phone_number TEXT,
    extension TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

COMMIT;
