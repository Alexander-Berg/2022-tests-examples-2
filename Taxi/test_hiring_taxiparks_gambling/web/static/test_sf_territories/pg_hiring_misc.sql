INSERT INTO hiring_taxiparks_gambling_salesforce.territories (
  sf_id,
  sf_name,
  is_deleted,
  rev,
  city_eng,
  city_rus,
  city_hiring,
  tariff_zone,
  region_id,
  extra,
  private_tariffs,
  rent_tariffs,
  employment_type,
  phone_country_code
) VALUES
(
  'deleted_not_hiring',
  'Anapa',
  TRUE,
  1,
  'Anapa',
  'Анапа',
  'Anapa',
  NULL,
  NULL,
  '{"IsHiring__c": false}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'deleted_hiring',
  'Irkutsk',
  TRUE,
  1,
  'Irkutsk',
  'Иркутск',
  'Irkutsk',
  NULL,
  NULL,
  '{"IsHiring__c": true}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'normal_not_hiring',
  'Omsk',
  FALSE,
  1,
  'Omsk',
  'Омск',
  'Omsk',
  'Omsk',
  '66',
  '{"IsHiring__c": false}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'normal',
  'Azov',
  FALSE,
  1,
  'Azov',
  'Азов',
  'azov',
  'azov',
  '11030',
  '{"IsHiring__c": true}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'normal_2',
  'Yakutsk',
  FALSE,
  1,
  'Yakutsk',
  'Якутск',
  'yakutsk',
  'yakutsk',
  '74',
  '{"IsHiring__c": true}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'normal_3_no_tariff_zone',
  'Balabanovo',
  FALSE,
  1,
  'Balabanovo',
  'Балабаново',
  NULL,
  NULL,
  '999',
  '{"IsHiring__c": true}'::jsonb,
  NULL,
  NULL,
  NULL,
  NULL
),
(
  'full_territory',
  'Moscow',
  FALSE,
  1,
  'Moscow',
  'Москва',
  'moscow',
  'moscow_zone',
  'moscow_region',
 NULL,
  '{"econom","comfort"}',
  '{"premier","elite"}',
  '{"self_employed"}',
  '+12345'
),
(
  'empty_territory',
  'Pripyat',
  FALSE,
  1,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL
);