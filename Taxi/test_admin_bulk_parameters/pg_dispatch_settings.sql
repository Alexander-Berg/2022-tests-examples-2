INSERT INTO dispatch_settings.parameters
    (field_name, schema)
VALUES
    (
        'PARAM_A',
        '{"type": "number"}'
),
    (
        'PARAM_B',
        '{"type": "number"}'
),
    (
        'PARAM_C',
        '{"type": "number"}'
),
    (
        'PARAM_D',
        '{"type": "number"}'
);

INSERT INTO dispatch_settings.actions
    (name)
VALUES
    ('test_action_1'),
    ('test_action_2'),
    ('test_action_3'),
    ('test_action_4'),
    ('test_action_5'),
    ('test_action_set'),
    ('test_action_remove'),
    ('test_action_add_items');

INSERT INTO dispatch_settings.allowed_actions
    (param_id, action_id, action_priority)
VALUES
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_A'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_1'),
        1
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_B'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_1'),
        1
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_B'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_2'),
        2
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_B'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_3'),
        0
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_C'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_2'),
        1
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_C'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_3'),
        2
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_C'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_4'),
        0
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_C'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_5'),
        3
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_D'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_set'),
        0
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_D'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_remove'),
        0
),
    (
        (SELECT id
        FROM dispatch_settings.parameters
        WHERE field_name = 'PARAM_D'),
        (SELECT id
        FROM dispatch_settings.actions
        WHERE name = 'test_action_add_items'),
        0
);
