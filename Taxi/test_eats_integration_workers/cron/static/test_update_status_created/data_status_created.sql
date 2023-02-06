INSERT INTO eats_integration_workers.integration_task
(
  id,
  place_id,
  type,
  status,
  reason,
  data_file_url,
  data_file_version,
  created_at
)
VALUES
(
  '5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4',
  'oBk3xjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g',
  'price',
  'created',
  'test_reason',
  'test_data_file_url',
  'test_data_file_version',
  '2000-01-01'
),
(
  '5GMix9mn36g1hlQtb40FoJ31231DYsCZuYrk4',
  'oBkasd3xjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g',
  'stock',
  'created',
  'test_reason',
  'test_data_file_url',
  'test_data_file_version',
  '2000-01-01'
),
(
  '5GMix9mn36g123hlQtb40FoJ3DYsCZuYrk4',
  'oBk3xasdjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g',
  'stock',
  'created',
  'test_reason',
  'test_data_file_url',
  'test_data_file_version',
  now()
);