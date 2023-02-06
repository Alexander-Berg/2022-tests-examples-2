INSERT INTO approvals_schema.drafts (
    created_by,
    comments,
    created,
    updated,
    description,
    approvals,status,
    version,
    request_id,
    run_manually,
    service_name,api_path,
    data,
    change_doc_id,
    apply_time,
    mode,
    tickets,
    summary,deferred_apply,
    is_multidraft,
    multidraft_id,
    scheme_type,
    tplatform_namespace
)
VALUES (
        'test_user',
        '[{"login": "asd",
        "comment": "ert"}]','2017-11-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp,
        'test','[]',
        'need_approval',
        1,
        '123',
        FALSE,
        'test_service',
        'test_api','{"service_name": "other_service_name"}',
        '234',
        '2017-11-01T01:10:00'::timestamp,'push',
        '[]',
        '{}',
        '2017-11-01T01:10:00'::timestamp,
        false,
        null::integer,
        'admin',
        'taxi'
        )
;
INSERT INTO approvals_schema.fields (
    service_name,
    api_path,
    path
)
VALUES (
        'test_service',
        'test_api',
        'name'
        ),
        (
        'test_service20',
        'test_api_to_delete',
        'name'
        )
;
INSERT INTO approvals_schema.field_values (
    field_id,draft_id,
    value,
    value_type
)
VALUES (
        1,
        1,
        'other_service_name',
        'string'
        )
;
