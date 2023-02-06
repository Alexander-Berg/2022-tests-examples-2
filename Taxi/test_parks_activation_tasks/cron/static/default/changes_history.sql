INSERT INTO parks_activation.change_history
(
    id, timestamp, park_id, field_name,
    before, after, reason, additional_data
)
VALUES
(
    1, '2010-01-01T0:00:00.000'::TIMESTAMPTZ, 'park1', 'field',
    'before', 'after', 'reason', 'additional_data'
),
(
    2, '2010-01-01T12:00:00.000'::TIMESTAMPTZ, 'park2', 'field',
    'before', 'after', 'reason', 'additional_data'
),
(
    3, '2010-02-01T12:00:01.000'::TIMESTAMPTZ, 'park3', 'field',
    'before', 'after', 'reason', 'additional_data'
);

