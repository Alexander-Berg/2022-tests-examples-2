INSERT INTO cashbox_integration.cashboxes
VALUES (
  'park_123',
  'id_abc123',
  'idemp_100500',
  '2016-06-22 19:10:25-07',
  '2016-06-22 19:10:25-07',
  'valid',
  FALSE,
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "super_park_group"
  }',
  '{
      "login": "M5a7svvcrnA7E5axBDY2sw==",
      "password": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
),
(
  'park_123',
  'id_abc456',
  'idemp_100000',
  '2016-06-22 19:10:25-07',
  '2016-06-22 19:10:25-07',
  'valid',
  TRUE,
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "super_park_group"
  }',
  '{
      "login": "M5a7svvcrnA7E5axBDY2sw==",
      "password": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
),
(
  'park_wo_current',
  'id_abc123',
  'idemp_777777',
  '2016-06-22 19:10:25-07',
  '2016-06-22 19:10:25-07',
  'deleted',
  FALSE,
  'atol_online',
  '{
      "tin_pd_id": "0123456789",
      "tax_scheme_type": "simple",
      "group_code": "super_park_group"
  }',
  '{
      "login": "M5a7svvcrnA7E5axBDY2sw==",
      "password": "dCKumeJhRuUkLWmKppFyPQ=="
  }'
);
