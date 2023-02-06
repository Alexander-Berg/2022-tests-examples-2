INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (2, 'other_service');

INSERT INTO tags
  (service_id, id, name)
VALUES
  (1, 10, 'a'),
  (2, 20, 'b');
