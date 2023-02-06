INSERT INTO clients_schema.consumers (name) VALUES ('a_consumer');
INSERT INTO clients_schema.consumers (name) VALUES ('b_consumer');
INSERT INTO clients_schema.consumers (name) VALUES ('filled_consumer');
INSERT INTO clients_schema.consumers (name) VALUES ('non_filled_consumer');

INSERT INTO clients_schema.consumer_kwargs
    (consumer, kwargs, metadata, library_version)
    VALUES
    ('a_consumer', '[{"name":"zone","type":"string"}]'::jsonb, NULL, NULL)
    ,('b_consumer', '[{"name":"zone_id","type":"integer"}]'::jsonb, NULL, NULL)
    ,('filled_consumer',
        '[{"name":"phone_id","type":"string"},{"name":"app_version","type":"application_version"},{"name": "application.store_country", "type": "string"}]'::jsonb,
        '{"library_version":"1.1.1"}'::jsonb, '1.1.1')
;
