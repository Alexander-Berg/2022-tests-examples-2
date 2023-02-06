INSERT INTO hiring_taxiparks_gambling_salesforce.territories (
  sf_id,
  sf_name,
  is_deleted,
  rev
) VALUES
(
  'must_delete',
  'Alderaan',
  FALSE,
  1
),
(
  'must_update',
  'Tatooine',
  FALSE,
  1
),
(
  'must_not_update',
  'Naboo',
  FALSE,
  1
),
(
  'must_not_hire',
  'Korriban',
  FALSE,
  1
),
(
  'must_hire',
  'Dantooine',
  FALSE,
  1
),
(
  'must_revive',
  'Death Star',
  TRUE,
  1
);

INSERT INTO hiring_taxiparks_gambling_salesforce.territories_last_update (
    id,
    last_update
) VALUES (
    1,
    '2019-01-01'
);

SELECT setval('hiring_taxiparks_gambling_salesforce.territories_revision', 123);
