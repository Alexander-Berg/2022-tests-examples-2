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
), (
    '5804fd71-c9a7-46c6-bba4-353ab6a2294a',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'test_tariff_filter', NULL,
    6,
    CAST('0.13' as DECIMAL(14, 4))
);
