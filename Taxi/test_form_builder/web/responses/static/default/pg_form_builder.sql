INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES
       ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas'),
       ('test_form_2', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.responses
VALUES
       (5, 'test_form', '2020-04-06T15:00:00.0Z'::TIMESTAMPTZ),
       (7, 'test_form', '2020-04-06T16:00:00.0Z'::TIMESTAMPTZ),
       (6, 'test_form_2', '2020-04-06T16:00:00.0Z'::TIMESTAMPTZ)
;
INSERT INTO form_builder.responses (id, form_code, submit_id)
VALUES (100, 'test_form', 'abc')
;

INSERT INTO form_builder.response_values
    (response_id, key, value, is_array, personal_data_type, field_label)
VALUES
       (5, 'a', '{"type": "string", "stringValue": "phone_id"}', false, 'phones', (NULL, 'phone_label')::form_builder.translatable),
       (5, 'b', '{"type": "integer", "integerValue": 1}', false, NULL, NULL),
       (5, 'c', NULL, FALSE, NULL, ('x.y', NULL)::form_builder.translatable),
       (100, 'a', '{"type": "string", "stringValue": "phone_id"}', FALSE, 'phones', (NULL, 'phone_label')::form_builder.translatable);
