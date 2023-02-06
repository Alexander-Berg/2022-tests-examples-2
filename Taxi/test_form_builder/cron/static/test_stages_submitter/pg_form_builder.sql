INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.responses VALUES (1, 'test_form'), (2, 'test_form'), (3, 'test_form'), (4, 'test_form');

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

INSERT INTO form_builder.partial_request_queue
    (response_id, status, method, url, tvm_service_id, form_code, stage_num, submit_id)
VALUES (1, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/ok', NULL, 'test_form', 1, 'a'),
       (3, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/fail', NULL, 'test_form', 1, 'c'),
       (4, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/fail/2', NULL, 'test_form', 1, 'd')
       ;

INSERT INTO form_builder.partial_request_queue
    (response_id, status, method, url, body_template, tvm_service_id, form_code, stage_num, submit_id, headers)
VALUES
       (2, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/ok/2', '{"a": {{ a }}, "submit_id": {{submit_id}}}', NULL, 'test_form', 1, 'b', ARRAY[('some', '{{submit_id}}')]::form_builder.submit_header[])
       ;
