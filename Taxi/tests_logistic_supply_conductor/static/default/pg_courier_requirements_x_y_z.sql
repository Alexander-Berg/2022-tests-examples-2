INSERT INTO logistic_supply_conductor.courier_requirements ("name", reason_title_for_courier, reason_subtitle_for_courier, expression, passthrough_revision)
VALUES
(
    'x', 'x_title', 'x_subtitle',
    '{"operator":"nor","tags":["one"],"expressions":[{"operator":"and","tags":["two"],"expressions":[{"operator":"nor","tags":["three"]}]}]}',
    NEXTVAL('courier_requirements_passthrough_revision_seq')
),
(
    'y', 'y_title', 'y_subtitle',
    '{"operator":"or"}',
    NEXTVAL('courier_requirements_passthrough_revision_seq')
),
(
    'z', 'z_title', 'z_subtitle',
    '{"operator":"nor"}',
    NEXTVAL('courier_requirements_passthrough_revision_seq')
);
