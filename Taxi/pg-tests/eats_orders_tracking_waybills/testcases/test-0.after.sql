INSERT INTO eats_orders_tracking.waybills
(waybill_ref, points, performer_info, order_nrs, chained_previous_waybill_ref, waybill_revision, created_at)
VALUES
('ref-1', '{}'::jsonb, '{}'::jsonb, array[]::TEXT[], NULL, 1, '2021-12-09T12:00:01.0000+03:00'::TIMESTAMPTZ);
