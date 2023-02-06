INSERT INTO combo_contractors.combo_batch (
  batch_id, order_id, updated
)
VALUES
  (
    'order_id0', 'order_id0', (NOW() AT TIME ZONE 'UTC') - INTERVAL '500 seconds'
  ),
  (
    'order_id0', 'order_id1', (NOW() AT TIME ZONE 'UTC') - INTERVAL '300 seconds'
  ),
  (
    'order_id0', 'order_id2', (NOW() AT TIME ZONE 'UTC') - INTERVAL '100 seconds'
  ),

  (
    'order_id3', 'order_id3', (NOW() AT TIME ZONE 'UTC') - INTERVAL '300 seconds'
  ),
  (
    'order_id3', 'order_id4', (NOW() AT TIME ZONE 'UTC') - INTERVAL '100 seconds'
  ),

  (
    'order_id5', 'order_id5', (NOW() AT TIME ZONE 'UTC') - INTERVAL '300 seconds'
  ),
  (
    'order_id5', 'order_id6', (NOW() AT TIME ZONE 'UTC') - INTERVAL '100 seconds'
  )
