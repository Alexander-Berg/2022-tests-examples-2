INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.responses (id, form_code, submit_id)
VALUES (1, 'test_form', 'submit_id-1'),
       (2, 'test_form', 'submit_id-2'),
       (3, 'test_form', 'submit_id-3'),
       (4, 'test_form', 'submit_id-4')
;

INSERT INTO form_builder.response_values (response_id, key, value, is_array, personal_data_type, value_type)
VALUES
       (1, 'a', '{"type": "string", "stringValue": "phone_id"}', false, 'phones', 'string'),
       (1, 'b', '{"type": "integer", "integerValue": 1}', false, NULL, 'integer'),
       (2, 'a', '{"type": "string", "stringValue": "A"}', false, NULL, 'string'),
       (2, 'b', '{"type": "integer", "integerValue": 1}', false, NULL, 'integer'),
       (3, 'a', '{"type": "string", "stringValue": "A"}', false, NULL, 'string'),
       (3, 'b', '{"type": "integer", "integerValue": 1}', false, NULL, 'integer'),
       (4, 'a', '{"type": "string", "stringValue": "A"}', false, NULL, 'string'),
       (4, 'b', '{"type": "integer", "integerValue": 1}', false, NULL, 'integer')
       ;

INSERT INTO form_builder.request_queue (response_id, status, method, url, headers, tvm_service_id, body_template)
VALUES (1, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/ok', ARRAY[('some', '{{submit_id}}')]::form_builder.submit_header[], NULL,
        '{"a": {{a}}, "b": {{b}}, "submit_id": {{submit_id}}}'),
       (2, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/ok/2', ARRAY[]::form_builder.submit_header[], NULL,
        '{"a": {{a}}, "b": {{b}}, "submit_id": {{submit_id}}}'),
       (3, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/fail', ARRAY[]::form_builder.submit_header[], NULL,
        '{"a": {{a}}, "b": {{b}}, "submit_id": {{submit_id}}}'),
       (4, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/fail/2', ARRAY[]::form_builder.submit_header[], NULL,
        '{"a": {{a}}, "b": {{b}}, "submit_id": {{submit_id}}}')
       ;
