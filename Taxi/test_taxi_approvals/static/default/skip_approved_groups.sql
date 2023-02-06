INSERT INTO approvals_schema.drafts (
    created_by,
    comments,
    created,
    updated,
    description,
    approvals,
    status,
    version,
    request_id,
    run_manually,
    service_name,
    api_path,
    data,
    change_doc_id,
    apply_time,
    mode,
    tickets,
    summary,
    deferred_apply,
    tplatform_namespace
)
VALUES (
        'test_login',
        '{}',
        '2017-11-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp,
        'test',
        '[]',
        'need_approval',
        1,
        '123',
        FALSE,
        'test_service',
        'test_route_several_groups',
        '{"managers": true}',
        '234',
        '2017-11-01T01:10:00'::timestamp,
        'poll',
        '[]',
        '{}',
        null::timestamp,
        null
        ),
        (
        'test_login',
        '{}',
        '2017-11-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp,
        'test',
        '[]',
        'need_approval',
        1,
        '124',
        FALSE,
        'test_service',
        'test_route_several_groups',
        '{"test_key": "test_value", "other_meta_data": "other_item_name_2"}',
        '235',
        '2017-11-01T01:10:00'::timestamp,
        'poll',
        '[]',
        '{}',
        null::timestamp,
        null
        )
;