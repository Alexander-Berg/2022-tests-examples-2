insert into secrets.templates (
    service_name,
    type_name,
    content,
    updated,
    pull_number,
    last_change_link
)
VALUES (
    'random_service',
    'secdist',
    '{"key": "value"}',
    150,
    11,
    null
);
