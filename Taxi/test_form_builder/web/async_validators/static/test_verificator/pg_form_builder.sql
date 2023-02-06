INSERT INTO form_builder.field_templates
    (id, name, has_choices, tags, is_array, author, value_type, personal_data_type)
VALUES
    (1, 'string', FALSE, '{}', FALSE, 'd1nbas', 'string', 'phones')
;


INSERT INTO form_builder.forms
    (code, conditions, default_locale, supported_locales, author)
VALUES
    ('form-1', '{}'::jsonb, 'ru', '{"ru"}'::text[], 'd1mbas')
;

INSERT INTO form_builder.stages
    (form_code)
VALUES
    ('form-1')
;

INSERT INTO form_builder.fields
    (code, visible, stage_id, template_id, label, async_validator, obligatory)
VALUES
    ('field-1', TRUE, 1, 1, (NULL, 'field-1'), ('sms_validator', 'field-1'), TRUE),
    ('field-2', TRUE, 1, 1, (NULL, 'field-2'), NULL, FALSE)
;

INSERT INTO form_builder.async_validation_states
    (form_code, field_code, submit_id, is_sent, is_valid, value, uuid)
VALUES
    ('form-1', 'field-1', 'submit_id', TRUE, NULL, '{"type": "string", "stringValue": "personal_id_2"}', '4699804c4d844566b56de06afa49e7c0')
;
