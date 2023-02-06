-- by this moment we treat ds.orders.status
--   'transporting' as active
--   'complete' as finished
-- here we forbid NULL for statuses
--   to prepare for use statuses from the app
UPDATE ds.orders
SET status = 'transporting'
WHERE status IS NULL;

UPDATE ds.orders
SET status = 'complete'
WHERE status = 'none';

ALTER TABLE ds.orders
ALTER COLUMN status SET NOT NULL;
