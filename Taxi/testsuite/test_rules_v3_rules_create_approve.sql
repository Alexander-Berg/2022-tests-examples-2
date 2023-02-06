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
);

ALTER SEQUENCE fees.draft_spec_id_seq RESTART WITH 9;

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
    2,
    'test_category',
    'test_category',
    'test_category',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2acf162a-b607-11ea-998e-07e60204cbcf',
    2,
    'hiring_category',
    'hiring_category',
    'hiring_category',
    'product_hiring',
    'detailed_product_hiring',
    'hiring',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2adf162a-b607-11ea-998e-07e60204cbcf',
    2,
    'fine_category',
    'fine_category',
    'fine_category',
    'product_fine',
    'detailed_product_fine',
    'fine',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
);

INSERT INTO fees.draft_rule (
    id,
    kind,
    starts_at,
    ends_at,
    draft_spec_id,
    fees,
    tariff_zone,
    tariff,
    withdraw_from_driver_account,
    tag,
    payment_type,
    cost_min,
    cost_max,
    hiring_type,
    hiring_age,
    fine_code
) VALUES (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    'software_subscription',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    3,
    '[{"fee": "100.1","subscription_level": "some_tariff"}]',
    'moscow',
    'econom',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
), (
    '2abf164a-b607-11ea-998e-07e60204cbcf',
    'software_subscription',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    4,
    '[{"fee": "100.2","subscription_level": "some_tariff"}]',
    'moscow',
    'econom',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
), (
    '2cbf164a-b607-11ea-998e-07e60204cbcf',
    'test_category',
    '2020-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    4,
    '{"percent": "0.02"}',
    'moscow',
    'econom',
    NULL,
    'tag',
    'payment_type',
    1,
    2,
    NULL,
    NULL,
    NULL
), (
    '2cbf164a-b603-11ea-998e-07e60204cbcf',
    'test_category',
    '2024-01-01T15:00:00+00:00',
    '2121-01-01T00:00:00+00:00',
    5,
    '{"percent": "0.02"}',
    'far_away',
    'econom',
    NULL,
    'tag',
    'payment_type',
    1,
    2,
    NULL,
    NULL,
    NULL
), (
    '2cbf164a-b604-11ea-998e-07e60204cbcf',
    'test_category',
    '2024-01-01T15:30:00+00:00',
    '2121-01-01T00:00:00+00:00',
    6,
    '{"percent": "0.02"}',
    'far_away',
    'econom',
    NULL,
    'tag',
    'payment_type',
    1,
    2,
    NULL,
    NULL,
    NULL
), (
    '2caf164a-b604-11ea-998e-07e60204cbcf',
    'hiring_category',
    '2024-01-01T15:30:00+00:00',
    '2121-01-01T00:00:00+00:00',
    7,
    '{"percent": "0.42"}',
    'moscow',
    'econom',
    NULL,
    'tag',
    'payment_type',
    1,
    2,
    'commercial_returned',
    128,
    NULL
), (
    '2cae164a-b604-11ea-998e-07e60204cbcf',
    'fine_category',
    '2024-01-01T15:30:00+00:00',
    '2121-01-01T00:00:00+00:00',
    8,
    '{"fee": "0.43"}',
    'moscow',
    'econom',
    NULL,
    'fine_tag',
    'fine_payment_type',
    1,
    2,
    NULL,
    NULL,
    'fine!!!'
);

INSERT INTO fees.rule(
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
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    'test_category',
    '2023-12-31T21:00:00+00:00', '2130-01-01T21:00:00+00:00',
    'far_away', 'econom',
    2,
    '{"percent": "0.42"}'
);

INSERT INTO fees.rule_tag(
    rule_id,
    tag
) VALUES (
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    'tag'
);

INSERT INTO fees.rule_payment_type(
    rule_id,
    payment_type
) VALUES (
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    'payment_type'
);

INSERT INTO fees.draft_rule_to_close (
    rule_id,
    draft_spec_id,
    ends_at
) VALUES (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    3,
    '2020-01-01T00:00:00+00:00'
), (
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    4,
    '2020-01-01T00:00:00+00:00'
), ( -- we want that this draft should newer ever applied
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    5,
    '2024-01-01T15:00:00+00:00'
), (
    'f3a0503d-3f30-4b43-8e30-71d77ebcaa1f',
    6,
    '2024-01-01T15:30:00+00:00'
);
