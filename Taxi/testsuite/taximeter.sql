INSERT INTO fees.draft_spec (id, change_doc_id) VALUES (101, 'Taximeter');
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
) SELECT
    '0e6c8361-c186-4cc2-a3a0-e282b249a8ed',
    id,
    'Taximeter',
    'Оброк за таксометр',
    'taximeter',
    'order',
    'gross_taximeter_payment',
    'absolute',
    '2000-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
FROM fees.draft_spec WHERE change_doc_id = 'Taximeter';
