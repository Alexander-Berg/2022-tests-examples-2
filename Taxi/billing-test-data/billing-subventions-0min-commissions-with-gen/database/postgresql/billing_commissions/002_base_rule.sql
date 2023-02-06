-- INSERT INTO fees.base_rule VALUES ('1715b67358f9478bb3fc15f828a4e6db', 'samara', NULL, NULL, 'corp', '2019-01-01 00:00:00+00', '2019-05-06 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 12000, '[]', 6, '2019-04-26 12:24:14.662+00')
INSERT INTO fees.base_rule VALUES (
    $1, -- id
    $2, -- zone
    $3, -- tariff_class
    NULL,
    $4, -- payment_type.
    '2019-01-01 00:00:00+00',
    '2020-01-01 00:00:00+00',
    'Europe/Moscow',
    'fixed_percent',
    $5, -- percent: '{"percent": 1200}',
    0, 150000000,
    '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}',
    ('{' ||
        '"acp": 0, ' ||
        '"agp": 0, ' ||
        '"hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, ' ||
        '"taximeter_payment": 10000, ' ||
        '"callcenter_commission_percent": 200' ||
    '}')::JSONB,
    0,
    '{"cost": 1500000, "percent": 700}',
    '[]',
    12000,
    '[]',
    6,
    '2019-04-26 12:24:14.662+00'
)
