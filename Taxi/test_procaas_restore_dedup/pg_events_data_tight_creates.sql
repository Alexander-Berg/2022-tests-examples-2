INSERT INTO processing.events(
        scope,
        queue,
        item_id,
        event_id,
        order_key,
        created,
        payload,
        idempotency_token,
        need_handle,
        updated,
        event_kind,
        is_archivable,
        due,
        is_malformed,
        extra_order_key,
        handling_order_key)
VALUES('testsuite',
       'foo',
       '14648896842964516938',
       'f80e6c8358bbd68ea62c058ec97ddfe3',
       0,
       '2021-06-16 23:16:31.880992+03'::timestamp with time zone,
       '{}',
       '3424234234-ba34-3421-aaaa-23424234234',
       True, -- need_handle
       '2021-06-16 23:16:31.954838+03'::timestamp with time zone,
       'user',
       False, -- is_archivable
       '2021-06-16 23:16:31.8814+03'::timestamp with time zone,
       False, -- is_malformed
       NULL,
       NULL);
