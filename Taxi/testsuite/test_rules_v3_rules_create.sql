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

INSERT INTO fees.category (
    id,
    draft_spec_id,
    name,
    description,
    kind,
    product,
    detailed_product,
    fields,
    starts_at,
    ends_at
) VALUES (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    3,
    'a123',
    'a123',
    'reposition',
    'product',
    'detailed_product',
    'core',
    '2000-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2abf162a-b617-11ea-998e-07e60204cbcf',
    3,
    'hiring',
    'hiring',
    'hiring',
    'product',
    'detailed_product',
    'hiring',
    '2000-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2adf162a-b617-11ea-998e-07e60204cbcf',
    3,
    'fine',
    'fine',
    'fine',
    'product_fine',
    'detailed_product_fine',
    'fine',
    '2000-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
     '2adf162a-b627-11ea-998e-07e60204cbcf',
     3,
     'taximeter',
     'taximeter',
     'taximeter',
     'product_taximeter',
     'detailed_product_taximeter',
     'absolute',
     '2000-01-01T21:00:00+00:00',
     '2119-01-01T21:00:00+00:00'
 );

insert INTO fees.rule(
    id,
    kind, -- description
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fees
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    'software_subscription',
    '2019-01-01T21:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    2,
    '[{"fee":"42.0001", "subscription_level": "level"}]'
), (
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    'software_subscription',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    '[{"fee":"42.0002", "subscription_level": "level"}]'
), (
    'f3a1503d-3f30-4a43-8e30-71d77ebcaa1f',
    'fine',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ekb', 'econom',
    2,
    '{"fee":"13313"}'
);

INSERT INTO fees.rule_fine_code (
    rule_id, fine_code
) VALUES (
    'f3a1503d-3f30-4a43-8e30-71d77ebcaa1f',
    'fine!!!'
)
