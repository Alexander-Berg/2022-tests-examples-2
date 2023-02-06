INSERT INTO fleet_feedback.polls
(
    "id",
    "type",
    "started_at",
    "offset",
    "periodicity",
    "enable",
    "distribution_duration",
    "filters",
    "type_settings",
    "created_at",
    "updated_at"
)
VALUES
(
    '1',
    'main',
    '2019-01-01T00:00:00+03:00',
    0,
    0,
    true,
    30,
    null,
    '{"questions": [{"id": "1", "text_key": "fleet_polls.questions_1"}, {"id": "2", "text_key": "fleet_polls.questions_2"}, {"id": "3", "text_key": "fleet_polls.questions_3"}], "labels": { "title": "fleet_polls.title", "button": "fleet_polls.button", "comment": "fleet_polls.comment"}}'::jsonb,
    '2019-01-01T00:00:00+03:00',
    '2019-01-01T00:00:00+03:00'
);
