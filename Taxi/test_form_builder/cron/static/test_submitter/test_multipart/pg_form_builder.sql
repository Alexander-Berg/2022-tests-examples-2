INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.responses VALUES (1, 'test_form'), (2, 'test_form');

INSERT INTO form_builder.response_values (response_id, key, value, is_array, value_type)
VALUES (1, 'test-file', '{"type": "file", "fileValue": "YWFhYQ=="}', FALSE, 'file'),
       (2, 'test-file', '{"type": "file", "fileValue": "YWFhYQ=="}', FALSE, 'file'),
       (2, 'a', '{"type": "string", "stringValue": "A"}', FALSE, 'string')
;

INSERT INTO form_builder.request_queue (response_id, status, method, url, headers, tvm_service_id, body_template, is_multipart)
VALUES (1, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/submit/file-only', ARRAY[]::form_builder.submit_header[], NULL, '', TRUE),
       (2, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/submit/file-n-json', ARRAY[]::form_builder.submit_header[], NULL, '{"a": {{a}}}', TRUE)
;
