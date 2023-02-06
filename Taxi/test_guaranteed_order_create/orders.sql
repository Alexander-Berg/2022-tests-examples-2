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
);
