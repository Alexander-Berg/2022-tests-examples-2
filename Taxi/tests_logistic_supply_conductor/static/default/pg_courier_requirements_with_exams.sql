INSERT INTO logistic_supply_conductor.courier_requirements ("name", reason_title_for_courier, reason_subtitle_for_courier, expression, passthrough_revision)
VALUES
(
    'foo', 'foo_title', 'foo_subtitle',
    '{"operator":"and","tags":["foo1","foo2"],"expressions":[{"operator":"nor","tags":["foo3","foo4"]}]}',
    NEXTVAL('courier_requirements_passthrough_revision_seq')
),
(
    'bar', 'bar_title', 'bar_subtitle',
    '{"operator":"or","tags":["bar1","bar2"],"exams":{"cool_dude":4}}',
    NEXTVAL('courier_requirements_passthrough_revision_seq')
);
