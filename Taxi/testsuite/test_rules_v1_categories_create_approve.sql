INSERT INTO fees.draft_spec(
    id,
    change_doc_id
) VALUES (
    2,
    'category_change_id'
), (
    3,
    'category_change_id1'
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
    2,
    'a123',
    'a123',
    'a123',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
);

INSERT INTO fees.draft_category (
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
    '2acf162a-b607-11ea-998e-07e60204cbcf',
    3,
    'a124',
    'a124',
    'a124',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2bcf162a-b607-11ea-998e-07e60204cbcf',
    3,
    'a123',
    'a123',
    'a123',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
);

INSERT INTO fees.draft_category_account(
    category_id,
    agreement,
    sub_account,
    currency,
    entity
) VALUES (
    '2acf162a-b607-11ea-998e-07e60204cbcf',
    'taxi/yandex-ride',
    'sub_account',
    'order_currency',
    'entity'
);
