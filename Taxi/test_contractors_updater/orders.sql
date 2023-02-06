INSERT INTO combo_contractors.customer_order (
  order_id, dbid_uuid, updated, taxi_status,
  destination, chunk_id, event_index, ready_status,
  tariff_class, tariff_zone, has_comment, source, calc_alternative_type,
  user_phone_id, plan_transporting_time, plan_transporting_distance,
  payment_type, corp_client_id, transporting_started_at, has_chain_parent,
  driving_started_at, combo_info
)
VALUES
  -- Possible combo contractors
  (
    'order_id0', 'dbid_uuid0', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.75)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.79)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:46:39',
    FALSE, '2001-9-9 01:36:39', NULL
  ),
  -- Non combo contractor
  (
    'order_id1', 'dbid_uuid1', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.71)', '',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Too close
  (
    'order_id4', 'dbid_uuid4', '2001-9-9 01:46:39',
    'transporting', '(37.66, 56.73)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 56.73)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Order has comment
  (
    'order_id2', 'dbid_uuid2', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    TRUE, '(37.66, 55.71)', '',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Finished order
  (
    'order_id3', 'dbid_uuid3', '2001-9-9 01:46:39',
    'complete', '(37.66, 55.71)',
    0, 0, 'finished', 'econom', 'moscow',
    FALSE, '(37.66, 55.71)', '',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- More than one combo-order per contractor
  (
    'order_id5', 'dbid_uuid5', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.76)', '',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:46:39', FALSE,
    '2001-9-9 01:36:39',
    '{
      "combo_info": {
        "category": "category0",
        "route": [
          {
            "order_id": "order_id6",
            "passed_at": "2001-09-09T01:26:39+0000",
            "position": [
              37.33,
              55.44
            ],
            "type": "start"
          },
          {
            "order_id": "order_id5",
            "passed_at": "2001-09-09T01:46:39+0000",
            "position": [
              37.77,
              55.88
            ],
            "type": "start"
          },
          {
            "order_id": "order_id0",
            "position": [
              37.11,
              55.22
            ],
            "type": "finish"
          },
          {
            "order_id": "order_id1",
            "position": [
              37.55,
              55.66
            ],
            "type": "finish"
          }
        ]
      }
    }'
  ),
  (
    'order_id6', 'dbid_uuid5', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.76)', '',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:26:39',
    FALSE, '2001-9-9 01:16:39', NULL
  ),
  -- Planning time is too short
  (
    'order_id7', 'dbid_uuid6', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.71)', 'combo',
    '507f1f77bcf86cd799439011', '43 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Planning distance is too short
  (
    'order_id8', 'dbid_uuid7', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.71)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 430,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Non-compliant phone id
  (
    'order_id9', 'dbid_uuid8', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.71)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.71)', 'combo',
    'non-compliant phone id', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', NULL, FALSE, NULL, NULL
  ),
  -- Contractor with chain order
  (
    'order_id10', 'dbid_uuid10', '2001-9-9 01:46:39',
    'transporting', '(37.66, 55.75)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.75)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:46:39',
    FALSE, '2001-9-9 01:36:39', NULL
  ),
  (
    'order_id11', 'dbid_uuid10', '2001-9-9 01:46:39',
    'driving', '(37.66, 55.75)',
    0, 0, 'pending', 'econom', 'moscow',
    FALSE, '(37.66, 55.75)', 'combo',
    '507f1f77bcf86cd799439011', '60 Seconds', 4300,
    'card', 'corp_client_id_ok', '2001-9-9 01:46:39',
    TRUE, '2001-9-9 01:46:39', NULL
  );
