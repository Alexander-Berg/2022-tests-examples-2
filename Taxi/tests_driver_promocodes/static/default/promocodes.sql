INSERT INTO promocodes.promocodes (
  id,
  series_name,
  entity_id,
  entity_type,
  can_activate_until,
  chatterbox_ticket,
  country,
  created_by,
  currency,
  description_key,
  title_key,
  is_created_by_service,
  is_seen,
  status,
  type,
  begin_at,
  end_at,
  created_at,
  updated_at
)
VALUES (
  'e084407133dc44d698b27aca76862f41',
  'test-series-1',
  'park_0_driver_0',
  'park_driver_profile_id'::promocodes.entity_type,
  '2020-06-01T09:00:00+00:00',
  'chatterbox1',
  'rus',
  'vdovkin',
  'RUB',
  'DriverPromocodes_TestKey',
  'DriverPromocodes_TestKey',
  false,
  false,
  'activated'::promocodes.promocode_status,
  'commission'::promocodes.series_type,
  '2020-06-01T00:00:00+00:00',
  '2020-06-03T00:00:00+00:00',
  '2020-06-01T11:00:01+0300',
  '2020-06-01T11:00:01+0300'
);


  
