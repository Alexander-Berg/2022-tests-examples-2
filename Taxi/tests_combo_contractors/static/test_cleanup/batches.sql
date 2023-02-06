INSERT INTO combo_contractors.combo_batch (
  batch_id, order_id, updated
)
VALUES
  -- Valid orders
  (
    'batch_id0', 'order_id0', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds'
  ),
  (
    'batch_id0', 'order_id1', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds'
  ),
  (
    'batch_id0', 'order_id2', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds'
  ),
  -- Order for cleanup
  (
    'batch_id1', 'order_id3', (NOW() AT TIME ZONE 'UTC') - INTERVAL '3 hours'
  ),
  (
    'batch_id1', 'order_id4', (NOW() AT TIME ZONE 'UTC') - INTERVAL '3 hours'
  ),
  (
    'batch_id1', 'order_id5', (NOW() AT TIME ZONE 'UTC') - INTERVAL '3 hours'
  )
