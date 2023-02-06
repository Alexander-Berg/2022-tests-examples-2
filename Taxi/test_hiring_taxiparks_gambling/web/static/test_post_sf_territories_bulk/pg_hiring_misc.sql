INSERT INTO hiring_taxiparks_gambling_salesforce.territories (
    sf_id,
    sf_name,
    is_deleted,
    rev,
    city_eng,
    city_rus,
    region_id,
    tariff_zone
)
VALUES
(
    'spb',
    'Saint-Petersburg',
    FALSE,
    1,
    'Saint-Petersburg',
    'Санкт-Петербург',
    '213',
    'tariff_zone_spb'
),
(
    'region_2',
    'Region 2',
    FALSE,
    1,
    'Moscow',
    'Москва',
    '2',
    'tariff_zone_msk'
),
(
    'del',
    'Deleted region',
    TRUE,
    1,
    'Deleted region',
    'Удаленый Регион',
    'del',
    'tariff_zone 3'
)
;
