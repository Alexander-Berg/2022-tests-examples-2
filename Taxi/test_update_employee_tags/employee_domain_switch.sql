INSERT INTO effrat_employees.employee (
  id,
  yandex_uid,
  login,
  domain,
  full_name,
  employment_status,
  employment_datetime
)
VALUES 
  (0, '1230000000000004', 'login0', 'lavka', 'Менятель Доменов', 'fired', '2022-01-01T01:01:01'),
  (1, '1230000000000004', 'login0', 'taxi', 'Менятель Доменов', 'in_staff', '2022-01-02T01:01:01');

INSERT INTO tags.tag
  (id, name, description, domain, color, updated_at)
values
  (0, 'test_taxi_tag0', 'taxi tag', 'taxi', Null, now()),
  (1, 'test_taxi_tag1', 'taxi tag', 'taxi', 'red', now()),
  (2, 'test_eats_tag2', 'eats tag', 'eats', 'blue', now()),
  (3, 'test_lavka_tag3', 'lavka tag', 'lavka', 'black', now());

INSERT INTO tags.entity
  (id, value)
VALUES
  (100, 'login0');

INSERT INTO tags.entity_to_tags
  (tag_id, entity_id)
VALUES
  (3, 100),
  (0, 100);
