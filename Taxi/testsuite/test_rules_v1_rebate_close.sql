INSERT INTO fees.draft_spec(
    change_doc_id
) VALUES (
    'zone1,zone2:some random change_doc_id'
), (
    'category_draft'
);

insert into fees.rebate_rule(
    id,
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fee
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    '2019-01-01T21:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'zone1,zone2:some random change_doc_id'
    ),
    CAST('42.0001' AS DECIMAL(14, 4))
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'zone1,zone2:some random change_doc_id'
    ),
    CAST('42.0001' AS DECIMAL(14, 4))
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcab1f',
    '2015-01-01T21:00:00+00:00', '2015-01-01T21:00:00+00:00',
    'spb', 'comfortplus',
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'zone1,zone2:some random change_doc_id'
    ),
    CAST('42.0001' AS DECIMAL(14, 4))
);
