INSERT INTO fleet.guaranteed_order (
  id,
  park_id,
  contractor_id,
  location_from,
  locations_to,
  client_booked_at,
  created_at,
  cancelled_at,
  processed_at,
  record_created_at,
  record_updated_at
)
VALUES (
  'order_id1',
  'park_id1',  
  'driver_id1',
  ARRAY[13.388378, 52.519894],
  ARRAY[ARRAY[13.396846, 52.502811], ARRAY[13.397283, 52.503113]],
  '2021-09-02T20:00:00Z',
  '2021-09-02T16:00:00Z',
  NULL,
  NULL,
  '2021-09-02T16:00:00Z',
  '2021-09-02T16:00:00Z'
),(
  'order_id2',
  NULL,  
  NULL,
  ARRAY[13.2984, 52.5103],
  ARRAY[ARRAY[13.2536, 52.4778], ARRAY[13.2736, 52.4602]],
  '2021-09-02T13:00:00Z',
  '2021-09-02T11:00:00Z',
  NULL,
  '2021-09-02T12:23:00Z',
  '2021-09-02T11:00:00Z',
  '2021-09-02T12:23:00Z'
);
