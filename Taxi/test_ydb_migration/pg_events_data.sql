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
       '961efda8b0ae413d8d646a1a8e451386',
       0,
       '2021-06-16 23:16:31.880992+03'::timestamp with time zone,
       '{"data": {"score": 3, "comment": "", "reasons": [], "order_id": "fab25968997d4dac8b350df84122eaa3", "phone_pd_id": "17dec53c8d0e43cd9646ec79a1432e6c", "order_provider_id": "cargo-claims"}, "kind": "kek"}',
       'idempotency_token_pg_data',
       True,
       '2021-06-16 23:16:31.954838+03'::timestamp with time zone,
       'user',
       False,
       '2021-06-16 23:16:31.8814+03'::timestamp with time zone,
       False,
       NULL,
       0);