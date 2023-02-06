INSERT INTO processing.events(
        scope,
        queue,
        item_id,
        event_id,
        order_key,
        payload,
        idempotency_token,
        need_handle,
        due)
VALUES
      ('testsuite',
       'foo',
       '0123456789',
       'abcdef000002',
       0,
       '{"kind": "etc"}',
       'idempotency_token_2',
       TRUE,
       '2021-01-01T00:00:00.000+03'::timestamp with time zone),
      ('testsuite',
       'foo',
       '012345678910',
       'abcdef000003',
       1,
       '{"kind": "etc"}',
       'idempotency_token_3',
       FALSE, -- already handled event
       '2021-01-01T00:00:00.000+03'::timestamp with time zone);
