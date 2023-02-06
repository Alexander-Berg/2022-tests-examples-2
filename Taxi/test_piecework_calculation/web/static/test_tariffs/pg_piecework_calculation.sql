INSERT INTO piecework.tariff(
    tariff_id,
    tariff_type,
    cost_conditions,
    benefit_conditions,
    countries,
    calc_night,
    calc_holidays,
    calc_workshifts,
    daytime_begins,
    daytime_ends,
    start_date
) VALUES (
    'current_tariff_id',
    'support-taxi',
    '{"rules": [{"cost_by_line": {"some_line": "123.45"}}]}'::JSONB,
    '{"__default__": {"benefits": "321.00"}}'::JSONB,
    ARRAY['rus', 'blr'],
    True,
    True,
    True,
    '07:30'::TIME,
    '21:30'::TIME,
    '2021-01-01'::DATE
);
