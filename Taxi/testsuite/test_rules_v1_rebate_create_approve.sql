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
    'far_away:change_doc_id5'
), (
    6,
    'far_away:change_doc_id6'
), (
    7,
    'moscow:hiring-change_doc_id7'
), (
    8,
    'moscow:fine-change_doc_id8'
), (
    9,
    'spb:future_rule_doc_id8'
);

ALTER SEQUENCE fees.draft_spec_id_seq RESTART WITH 9;

INSERT INTO fees.draft_rebate_rule (
    id,
    starts_at,
    ends_at,
    draft_spec_id,
    fee,
    tariff_zone,
    tariff
) VALUES (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    3,
    '100.1',
    'moscow',
    'econom'
), (
    '2abf164a-b607-11ea-998e-07e60204cbcf',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    4,
    '100.2',
    'moscow',
    'econom'
), (
    '2cbf164a-b607-11ea-998e-07e60204cbcf',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    4,
    '0.02',
    'moscow',
    NULL
), (
    '2cbf164a-b603-11ea-998e-07e60204cbcf',
    '2024-01-01T15:00:00+00:00',
    '2121-01-01T00:00:00+00:00',
    5,
    '0.02',
    'far_away',
    'econom'
), (
    '2cbf164a-b604-11ea-998e-07e60204cbcf',
    '2024-01-01T15:30:00+00:00',
    '2121-01-01T00:00:00+00:00',
    6,
    '0.02',
    'far_away',
    'econom'
), (
    '2caf164a-b604-12ea-998e-07e60204cbcf',
    '2024-01-01T15:30:00+00:00',
    '2121-01-01T00:00:00+00:00',
    7,
    '0.42',
    'spb',
    NULL
), (
    '2cae164a-b604-11ea-998e-07e60204cbcf',
    '2024-01-01T15:30:00+00:00',
    NULL,
    8,
    '0.43',
    'moscow',
    'econom'
), (
    '2caf164a-b604-12eb-998e-07e60204cbcf',
    '2020-01-01T15:30:00+00:00',
    NULL,
    9,
    '0.42',
    'spb',
    'econom'
);

INSERT INTO fees.rebate_rule(
    id,
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fee
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    '2019-01-01T21:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    2,
    '42.0001'
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    '42.0002'
), (
    'f3a0503d-3f30-4a43-8e30-72d77ebcaa1f',
    '2030-01-01T21:00:00+00:00', NULL,
    'spb', 'econom',
    2,
    '42.0001'
), (
    'f3a0503d-3f40-4a43-8e30-71d77ebcaa1f',
    '2012-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', NULL,
    2,
    '42.0002'
), (
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    '2023-12-31T21:00:00+00:00', '2130-01-01T21:00:00+00:00',
    'far_away', 'econom',
    2,
    '0.42'
);
