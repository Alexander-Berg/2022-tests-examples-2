INSERT INTO fees.draft_spec(
    change_doc_id
) VALUES (
    'category_change_id'
), (
    'category_change_id1'
);

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
    (
        SELECT id FROM fees.draft_spec
        WHERE change_doc_id = 'category_change_id'
    ),
    'a123',
    'a123',
    'a123',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
);
