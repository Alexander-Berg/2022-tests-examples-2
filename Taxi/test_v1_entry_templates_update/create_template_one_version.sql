INSERT INTO billing_settings.billing_settings (
    name, value, namespace, project, version, start_date, end_date
) VALUES (
             'test_entry_templates_update',
             '{"actions": [],"entries": [],"examples": [{"context": {}, "expected_actions": [],"expected_entries": [] }]}',
             'entry_templates',
             'taxi',
             1,
             '2021-01-01T00:00:00+00:00',
             null
         )
