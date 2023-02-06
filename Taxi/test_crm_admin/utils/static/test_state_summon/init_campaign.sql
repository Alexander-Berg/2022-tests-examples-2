INSERT INTO crm_admin.campaign
(
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
    motivation_methods,
    settings
)
VALUES
(
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
    '{workshifts}',
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
    ]')::jsonb
);
