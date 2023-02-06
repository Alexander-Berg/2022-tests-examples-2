-- defaults
-- create software subscription category
INSERT INTO fees.draft_spec (
    change_doc_id, approvers, initiator, ticket
) VALUES (
             'TAXIBILLING-3985 (maksimzubkov). Create software subscription',
             'maksimzubkov, system',
             'maksimzubkov',
             'TAXIBILLING-3985'
         );

INSERT INTO fees.category (
    id, draft_spec_id, name, kind, description,
    product, detailed_product, fields, starts_at, ends_at
) SELECT
      '5d4378cb-c74c-ad34-e7d7-fa32c61f0f3b',
      id,
      'Opteum',
      'software_subscription',
      'Opteum commission',
      'order',
      'gross_software_subscription_fee',
      'software_subscription',
      '2020-09-01T00:00:00+03:00',
      '2120-09-01T00:00:00+03:00'
FROM fees.draft_spec
WHERE
        change_doc_id = 'TAXIBILLING-3985 (maksimzubkov). Create software subscription';
-- defaults
