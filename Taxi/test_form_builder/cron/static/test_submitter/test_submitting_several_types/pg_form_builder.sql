INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.responses VALUES (1, 'test_form');

INSERT INTO form_builder.request_queue (response_id, status, method, url, headers, tvm_service_id, body_template)
VALUES (1, 'PENDING'::form_builder.submit_status, 'POST', '$mockserver/test', ARRAY[]::form_builder.submit_header[], NULL,
        '{"a": {{a}}, "b": {{b}}}')
       ;
