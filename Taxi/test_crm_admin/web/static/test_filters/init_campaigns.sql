INSERT INTO crm_admin.segment
(
    yql_shared_url,
    yt_table,
    aggregate_info,
    mode,
    control,
    created_at
)
VALUES
(
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    salt,
    error_code,
    error_description,
    created_at,
    updated_at,
    qs_major_version
)
VALUES
(
    1,  -- id
    'Первая кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Открыт',
    'salt',
    'SOME_ERROR',  -- error_code
    ('{"message": "content"}')::jsonb,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    0
);


INSERT INTO crm_admin.campaign
(
    id,
    name,
    specification,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    settings,
    ticket,
    ticket_status,
    creative,
    test_users,
    segment_id,
    created_at,
    updated_at,
    qs_major_version
)
VALUES
(
    6,  -- id
    'Шестая кампания',
    'Описание шестой кампании',
    'Driver',
    'Направление или тип шестой кампании',
    'Тип или подтип шестой кампании',
    True,
    'NEW',
    'user6',
    ('[
          {
            "fieldId": "field_1",
            "value": "value_1"
          },
          {
            "fieldId": "field_2",
            "value": "value_2"
          },
          {
            "fieldId": "field_3",
            "value": "value_3"
          },
          {
            "fieldId": "field_4",
            "value": false
          },
          {
            "fieldId": "field_5",
            "value": 5
          },
          {
            "fieldId": "field_6",
            "value": 66.6
          }
    ]')::jsonb,
    'Тикет6',
    'Открыт',
    'Шестой креатив',
    ARRAY ['test1_user1', 'test1_user2'],
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    0
),
(
    7,  -- id
    'running segment task',
    'specification',
    'Driver',
    'trend',
    'kind',
    True,
    'SEGMENT_CALCULATING',
    'user',
    ('[
          {
            "fieldId": "field_1",
            "value": "value_1"
          }
    ]')::jsonb,
    'ticket',
    'open',
    'creative',
    null,
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    1
),
(
    8,  -- id
    'running segment task',
    'specification',
    'Driver',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    ('[
          {
            "fieldId": "field_1",
            "value": "value_1"
          }
    ]')::jsonb,
    'ticket',
    'open',
    'creative',
    null,
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    1
);

INSERT INTO crm_admin.audience
VALUES
('User', 'Пользователи'),
('Driver', 'Водители')
;

INSERT INTO crm_admin.quicksegment_schemas (
    audience,
    major_ver,
    minor_ver,
    name,
    format,
    body,
    created_at
)
VALUES
(
    'User',
    0,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "field_1"}, {"id": "field_2"}, {"id": "field_3"}, {"id": "field_4"}, {"id": "field_5"}, {"id": "field_6"}, {"id": "field", "serverYtTableValidation": {"pathVerification": true, "tableAttrName": "^[a-zA-Z0-9_]+$", "requiredAttrs": [{"required_attr": "int32"}, {"required_attr2": "int32", "required_attr3": "int32"}], "attrAcceptableDataType": ["int32", "string"], "tableData": true}}]',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "field_1"}, {"id": "field_2"}, {"id": "field_3"}, {"id": "field_4"}, {"id": "field_5"}, {"id": "field_6"}, {"id": "field"}]',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    1,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "field_1"}, {"id": "field_2"}, {"id": "field_3"}, {"id": "field_4"}, {"id": "field_5"}, {"id": "field_6"}, {"id": "field", "serverYtTableValidation": {"pathVerification": true}}]',
    '2020-11-24 01:00:00'
);
