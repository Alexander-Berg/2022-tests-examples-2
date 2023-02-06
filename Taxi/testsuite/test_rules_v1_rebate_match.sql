INSERT INTO fees.draft_spec(
    id,
    change_doc_id
) VALUES (
    2,
    'zone1,zone2:some random change_doc_id'
), (
    3,
    'moscow:change_doc_id'
), (
    4,
    'moscow:change_doc_id1'
), (
    5,
    'reposition draft'
), (
    6,
    'fine_draft'
);

ALTER SEQUENCE fees.draft_spec_id_seq RESTART WITH 99;

INSERT INTO fees.rebate_rule(
    id,
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fee
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    '2019-01-01T21:00:00+00:00', NULL,
    'moscow', 'econom',
    2,
    CAST(42 as DECIMAL(14, 4))
), (
    '2abf062a-b607-11ea-998e-07e60204cbdf',
    '2019-01-01T21:00:00+00:00', NULL,
    'moscow', NULL,
    2,
    CAST(24 as DECIMAL(14, 4))
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    CAST('42.0002' as DECIMAL(14, 4))
), (
    'f3a0603d-3f30-4a43-8e30-71d77ebcaa1f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    CAST('42.42' as DECIMAL(14, 4))
), (
    'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ekb', 'econom',
    2,
    CAST('0.13' as DECIMAL(14, 4))
), (
    'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ekb', 'comfortplus',
    6,
    CAST('0.13' as DECIMAL(14, 4))
), (
    '703bffab-b3d0-426e-9f40-137847d480d2',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'test_tariff_filter', 'comfortplus',
    6,
    CAST('0.13' as DECIMAL(14, 4))
);


INSERT INTO fees.base_rule (
    rule_id,
    tariff_zone, tariff, tag, payment_type,
    starts_at, ends_at, time_zone,
    rule_type, fee,
    min_order_cost, max_order_cost,
    billing_values,
    rates,
    cancellation_percent, expiration,
    branding_discounts,
    vat,
    changelog,
    draft_spec_id
) VALUES (
    'some_fixed_percent_commission_contract_id_in_future_end',
    'moscow', null, null, 'corp',
    '2018-12-31T20:00:00+03:00', '2030-01-01T00:00:00.789+03:00', 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
);
