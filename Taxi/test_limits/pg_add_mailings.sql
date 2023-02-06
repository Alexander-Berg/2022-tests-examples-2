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
    'TITLE{}',
    'MESSAGE{}',
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
    deleted_at,
    updated_at
) VALUES (
    'MAILING-01',
    'PARK-01',
    'TEMPLATE-01',
    '2022-01-02T12:00:00+00:00',
    '999',
    NULL,
    NULL,
    'DELETED_BY_DISPATCHER',
    NULL,
    '2022-01-02T12:10:00+00:00',
    '2022-01-02T12:10:00+00:00'
);
