INSERT INTO internal_b2b.staff_compensation(
    login,
    type_compensation,
    in_perimeter,
    is_dismissed,
    is_active_compensation,
    cab_id
)
VALUES (
    'cat',
    'taxi',
    true,
    false,
    true,
    0
), (
    'dog',
    'taxi',
    true,
    false,
    true,
    1
), (
    'fox',
    'taxi',
    true,
    true,
    false,
    2
), (
    'fox',
    'plus',
    true,
    false,
    false,
    3
), (
    'fox',
    'plus',
    true,
    false,
    true,
    4
), (
    'fox',
    'taxi',
    false,
    false,
    false,
    5
);

INSERT INTO internal_b2b.staff_persons(
    id,
    login,
    department_group_id,
    department_group_ancestors_id,
    official
)
VALUES (
    0,
    'cat',
    119530,
    '{"value": 0}'::jsonb,
    '{"is_dismissed": false}'::jsonb
), (
    1,
    'dog',
    119530,
    '{"value": 1231}'::jsonb,
    '{"is_dismissed": false}'::jsonb
), (
    2,
    'fox',
    119530,
    '{"value": 1}'::jsonb,
    '{"is_dismissed": true}'::jsonb
), (
    3,
    'fox',
    0,
    '{"value": 211914}'::jsonb,
    '{"is_dismissed": true}'::jsonb
), (
    4,
    'Mouse',
    119530,
    '{"value": 119530}'::jsonb,
    '{"is_dismissed": false}'::jsonb
)
