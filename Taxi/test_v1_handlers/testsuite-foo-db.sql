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
VALUES('testsuite',
       'foo',
       '0123456789',
       'abcdef000002',
       0, -- will be updated to 2 by restore
       '{"kind": "etc"}',
       'idempotency_token_2',
       FALSE,
       '2021-01-01T00:00:00.000+03'::timestamp with time zone);
