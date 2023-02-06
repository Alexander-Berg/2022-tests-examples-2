INSERT INTO config.processors
(
  processor_id,
  code,
  created_at
)
VALUES
(
  'reposition_relocator_id',
  'reposition-relocator',
  NOW()
)
;

INSERT INTO config.operations
(
  operation_id,
  processor_id,
  code,
  created_at
)
VALUES
(
  'make_offer_id',
  'reposition_relocator_id',
  'make_offer',
  NOW()
)
;

INSERT INTO config.graph_operations
(
  graph_operation_id,
  operation_id,
  created_at
)
VALUES
(
  'graph_make_offer_id',
  'make_offer_id',
  NOW()
);
