INSERT INTO supportai.debug (project_slug, chat_id, iteration_number, expire_at, debug_json)
VALUES
('test_project', '1234', 1, '2121-08-02T10:00:00', '{"blocks": []}'),
('test_project', '1234', 2, '2121-08-02T10:00:00', '{"blocks": []}');

ALTER SEQUENCE supportai.debug_id_seq RESTART WITH 3;
