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
    'fox1',
    'plus',
    true,
    false,
    false,
    3
), (
    'fox2',
    'plus',
    true,
    false,
    true,
    4
), (
    'fox3',
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
    '[0]'::jsonb,
    '{"is_dismissed": false}'::jsonb
), (
    1,
    'dog',
    119530,
    '[1231]'::jsonb,
    '{"is_dismissed": false}'::jsonb
), (
    2,
    'fox',
    119530,
    '[1]'::jsonb,
    '{"is_dismissed": true}'::jsonb
), (
    3,
    'fox1',
    0,
    '[211914]'::jsonb,
    '{"is_dismissed": true}'::jsonb
), (
    4,
    'fox2',
    119530,
    '[119530]'::jsonb,
    '{"is_dismissed": false}'::jsonb
), (
    5,
    'fox3',
    119530,
    '[119530]'::jsonb,
    '{"is_dismissed": true}'::jsonb
), (
    123,
    'danil-yacenko',
    82368,
    '[962, 211913, 119530, 34693, 104424, 127469, 128316]'::jsonb,
    '{"is_dismissed": false}'::jsonb
)
