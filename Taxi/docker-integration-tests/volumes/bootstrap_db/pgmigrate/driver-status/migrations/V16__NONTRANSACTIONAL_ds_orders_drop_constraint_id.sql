ALTER TABLE ds.orders DROP CONSTRAINT orders_pkey;
CREATE INDEX CONCURRENTLY ds_orders_id_index ON ds.orders(id);
