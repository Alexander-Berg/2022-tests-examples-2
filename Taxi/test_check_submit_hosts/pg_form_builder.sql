INSERT INTO form_builder.forms (code, conditions, default_locale, supported_locales, author)
VALUES ('test_form', '{}'::JSONB, ARRAY['ru'], ARRAY['ru'], 'd1mbas');

INSERT INTO form_builder.submit_options (id, form_code, method, url, body_template, headers, host, port)
VALUES (1, 'test_form', 'post', 'http://test.url.com/test-path/', '', '{}', 'test.url.com', 80),
       (2, 'test_form', 'post', 'http://test.url.com/test-path/', '', '{}', 'test.url.com', NULL),
       (3, 'test_form', 'post', 'http://test.url.com/test-path/', '', '{}', NULL, 80);
