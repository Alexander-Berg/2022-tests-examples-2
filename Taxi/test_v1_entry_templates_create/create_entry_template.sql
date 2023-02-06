INSERT INTO billing_settings.billing_settings (
    name, value, namespace, project, version, start_date
) VALUES (
             'test_entry_template_creation',
             '{"actions": [],"entries": [],"examples": []}',
             'entry_templates',
             'taxi',
             1,
             '2021-01-01T00:00:00+00:00'
         );
