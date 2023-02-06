INSERT INTO fees.draft_spec(
    id,
    change_doc_id
) VALUES (
    2,
    'zone1,zone2:some random change_doc_id'
), (
    3,
    'category_draft'
);

ALTER SEQUENCE fees.draft_spec_id_seq RESTART WITH 4;

insert INTO fees.rebate_rule(
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
    'f3a1503d-3f30-4a43-8e30-71d77ebcaa1f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ekb', 'econom',
    2,
    '13313'
);

