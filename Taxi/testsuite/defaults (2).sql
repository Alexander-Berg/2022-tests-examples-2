-- defaults
INSERT INTO billing_settings.billing_settings (
    name, value, namespace, project, version, start_date
) VALUES (
         'some_config_name',
         '{"actions": [],"entries": [],"examples": [{"context": {}, "expected_actions": [],"expected_entries": [] }]}',
         'entry_templates',
         'taxi',
         1,
         '2021-01-01T00:00:00+00:00'
     );
-- defaults
