INSERT INTO billing_settings.billing_settings (
    name, value, namespace, project, version, start_date
) VALUES (
             'some_broken_config_name',
             '{"actions": "some_broken_data"}',
             'entry_templates',
             'taxi',
             1,
             '2020-01-01T00:00:00+00:00'
         );
