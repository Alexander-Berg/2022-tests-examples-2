INSERT INTO billing_settings.billing_settings (
    name, value, namespace, project, version, start_date, end_date
) VALUES (
             'empty_template',
             '{"actions": [],"entries": [],"examples": [{"context": {"version": "old_version"}, "expected_actions": [],"expected_entries": [] }]}',
             'entry_templates',
             'taxi',
             1,
             '2007-01-01T00:00:00+00:00',
             '2021-01-01T00:00:00+00:00'
         ),
         (
             'empty_template',
             '{"actions": [],"entries": [],"examples": [{"context": {"version": "new_version"}, "expected_actions": [],"expected_entries": [] }]}',
             'entry_templates',
             'taxi',
             2,
             '2021-01-01T00:00:00+00:00',
             null
         ),
        (
            'test_store_remittance_purchase',
            '{ "actions": [ { "$func": "send_balance_update", "$vars": {} }, { "$func": "send_income_entries", "$vars": {} } ], "entries": [ { "agreement_id": "taxi/yandex_marketing", "amount": { "$context": "amount" }, "currency": { "$context": "currency" }, "details": { "alias_id": { "$format": "noorder/store_remittance_payment/{payment_id}" }, "payment_id": { "$context": "payment_id" } }, "entity_external_id": { "$format": "taximeter_driver_id/{park_id}/{driver_uuid}" }, "event_at": { "$context": "event_at" }, "sub_account": "buyer/remittance_payment_inc_vat" }, { "agreement_id": "taxi/yandex_marketing", "amount": { "$context": "amount" }, "currency": { "$context": "currency" }, "details": { "alias_id": { "$format": "noorder/store_remittance_payment/{payment_id}" }, "driver": { "driver_uuid": { "$context": "driver_uuid" } }, "payment_id": { "$context": "payment_id" } }, "entity_external_id": { "$format": "taximeter_park_id/{park_id}" }, "event_at": { "$context": "event_at" }, "sub_account": "buyer/remittance_payment_inc_vat" }, { "agreement_id": "taxi/driver_balance", "amount": { "$context": "amount" }, "currency": { "$context": "currency" }, "details": {}, "entity_external_id": { "$format": "taximeter_driver_id/{park_id}/{driver_uuid}" }, "event_at": { "$context": "event_at" }, "sub_account": "total" } ], "examples": [ { "context": { "amount": "-100.0000", "currency": "RUB", "driver_uuid": "<some_driver_uuid>", "event_at": "2021-10-05T00:00:00.000000+00:00", "park_id": "<some_park_id>", "payment_id": "<store_payment_id>" }, "expected_actions": [ { "func": "send_balance_update", "keywords": {} }, { "func": "send_income_entries", "keywords": {} } ], "expected_entries": [ { "agreement_id": "taxi/yandex_marketing", "amount": "-100.0000", "currency": "RUB", "details": { "alias_id": "noorder/store_remittance_payment/<store_payment_id>", "payment_id": "<store_payment_id>" }, "entity_external_id": "taximeter_driver_id/<some_park_id>/<some_driver_uuid>", "event_at": "2021-10-05T00:00:00.000000+00:00", "sub_account": "buyer/remittance_payment_inc_vat" }, { "agreement_id": "taxi/yandex_marketing", "amount": "-100.0000", "currency": "RUB", "details": { "alias_id": "noorder/store_remittance_payment/<store_payment_id>", "driver": { "driver_uuid": "<some_driver_uuid>" }, "payment_id": "<store_payment_id>" }, "entity_external_id": "taximeter_park_id/<some_park_id>", "event_at": "2021-10-05T00:00:00.000000+00:00", "sub_account": "buyer/remittance_payment_inc_vat" }, { "agreement_id": "taxi/driver_balance", "amount": "-100.0000", "currency": "RUB", "details": {}, "entity_external_id": "taximeter_driver_id/<some_park_id>/<some_driver_uuid>", "event_at": "2021-10-05T00:00:00.000000+00:00", "sub_account": "total" } ] } ]}',
           'entry_templates',
            'taxi',
            1,
            '2022-01-01T00:00:00+00:00',
            null
        );
