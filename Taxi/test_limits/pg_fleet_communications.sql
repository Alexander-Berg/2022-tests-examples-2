INSERT INTO fleet_communications.mailing_templates (
    id,
    park_id,
    work_rule_ids,
    driver_statuses,
    car_categories,
    car_amenities,
    affiliation_partner_sources,
    deptrans_statuses,
    included_contractor_ids,
    excluded_contractor_ids,
    title,
    message,
    created_at,
    created_by
) VALUES (
    'TEMPLATE-01',
    'PARK-01',
    '{"WORK_RULE-01"}',
    '{"busy"}',
    '{"econom"}',
    '{"wifi"}',
    '{"none"}',
    '{"permanent"}',
    '{"CONTRACTOR-03", "CONTRACTOR-04"}',
    '{"CONTRACTOR-04"}',
    'TITLE',
    'MESSAGE',
    '2022-01-01T12:00:00+00:00',
    '999'
);

INSERT INTO fleet_communications.mailings (
    id,
    park_id,
    template_id,
    created_at,
    created_by,
    sent_at,
    sent_to_number,
    status,
    deleted_by,
    deleted_at
) VALUES (
    'MAILING-01',
    'PARK-01',
    'TEMPLATE-01',
    '2022-01-01T12:00:00+00:00',
    '999',
    '2022-01-01T12:00:00+00:00',
    555,
    'SENT',
    NULL,
    NULL
), (
    'MAILING-02',
    'PARK-01',
    'TEMPLATE-01',
    '2022-01-01T13:10:00+00:00',
    '999',
    '2022-01-01T13:10:00+00:00',
    555,
    'SENT',
    NULL,
    NULL
), (
    'MAILING-03',
    'PARK-01',
    'TEMPLATE-01',
    '2022-01-01T14:00:00+00:00',
    '999',
    NULL,
    NULL,
    'CREATED',
    NULL,
    NULL
);
