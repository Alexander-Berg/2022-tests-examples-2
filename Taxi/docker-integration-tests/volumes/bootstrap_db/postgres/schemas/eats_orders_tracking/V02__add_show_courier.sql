/* V2 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

-- Флажок - показывать ли курьера на карте. Задача: EDAEATERS-17
ALTER TABLE eats_orders_tracking.display_templates
    ADD COLUMN show_courier BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT;
