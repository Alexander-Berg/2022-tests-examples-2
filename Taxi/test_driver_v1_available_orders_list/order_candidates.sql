INSERT INTO fleet.order_candidates (
  order_id, 
  candidates, 
  updated_at
) 
VALUES (
  'order_id', 
  ARRAY[ARRAY['park_id', 'driver_id'], ARRAY['park_id', 'driver_id1']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_without_comment', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_without_comment_and_distance', 
  ARRAY[ARRAY['park_id', 'driver_id'], ARRAY['park_id', 'driver_id1'], ARRAY['park_id1', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_park_id_is_not_null', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_contractor_id_is_not_null', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_source_park_id_is_not_null', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_contractor_id_park_id_is_not_null', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_invalid_booked_at', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_invalid_booked_at1', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_processed', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_cancelled', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_invalid_candidates_empty_candidates', 
  ARRAY[ARRAY['park_id', 'driver']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_invalid_candidates_empty_candidates1', 
  ARRAY[ARRAY['park_id1', 'driver_id']], 
  '2021-09-02T17:00:00Z'
), (
  'order_id_empty_locations_to', 
  ARRAY[ARRAY['park_id', 'driver_id']], 
  '2021-09-02T19:00:00Z'
)
;
