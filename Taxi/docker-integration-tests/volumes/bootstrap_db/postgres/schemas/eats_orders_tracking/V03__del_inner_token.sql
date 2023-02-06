/* V3 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

-- База данных пока пустая, поэтому можем потребовать NOT NULL и не указывать DEFAULT.
ALTER TABLE eats_orders_tracking.orders
    ADD COLUMN eater_id TEXT NOT NULL;

CREATE INDEX orders_eater_id_idx ON eats_orders_tracking.orders (eater_id);

-- Индексы eater_order_refs_eater_id_idx и inner_token_order_refs_inner_token_idx
-- удалятся автоматически вместе с таблицами.
DROP TABLE eats_orders_tracking.eater_order_refs;
DROP TABLE eats_orders_tracking.inner_token_order_refs;

COMMIT;
