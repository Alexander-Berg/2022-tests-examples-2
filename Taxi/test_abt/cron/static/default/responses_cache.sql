INSERT INTO
  abt.responses_cache (
    id,
    conditions,
    precomputes_tables_ids,
    data
  )
VALUES
  (
    'hash_1',
    '{}'::jsonb,
    '{1,2,3}'::int[],
    '{}'::jsonb
  );
