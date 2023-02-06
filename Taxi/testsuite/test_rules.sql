INSERT INTO fees.draft_spec(
    change_doc_id
) VALUES (
    'zone1,zone2:some random change_doc_id'
);

insert into fees.rule(
    id,
    kind, -- description
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fees
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    'software_subscription',
    '2020-01-01T21:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'zone1,zone2:some random change_doc_id'
    ),
    '{"fee":"42.0001"}'
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    'software_subscription',
    '2021-01-01T21:00:00+00:00', '2022-01-01T21:00:00+00:00',
    'spb', 'econom',
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'zone1,zone2:some random change_doc_id'
    ),
    '{"fee":"42.0002"}'
);
