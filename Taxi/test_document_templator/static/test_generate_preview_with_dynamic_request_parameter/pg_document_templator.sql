INSERT INTO "document_templator"."templates" (id,
                                              version,
                                              dependencies,
                                              base_template_id,
                                              name,
                                              description,
                                              group_id,
                                              css_style,
                                              created_by,
                                              created_at,
                                              modified_by,
                                              modified_at,
                                              params,
                                              param_settings,
                                              items,
                                              item_settings,
                                              requests,
                                              request_settings,
                                              enumerators)
VALUES ('111111111111111111111111',
        0,
        NULL,
        NULL,
        'test',
        'test',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        '[]'::JSONB,
        '[]'::JSONB,
        '[
          {
            "content": "<span data-variable=\"req.test\" data-request-id=\"\"/>",
            "description": "",
            "persistent_id": "999999999999999999999999"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "999999999999999999999999",
            "version": 1
          }
        ]'::JSONB,
        '[
          {
            "name": "req",
            "request_id": "111111111111111111111111"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "req"
          }
        ]'::JSONB,
        '[]'::JSONB);

INSERT INTO "document_templator"."requests" (id,
                                             name,
                                             description,
                                             endpoint_name,
                                             body_schema,
                                             response_schema,
                                             query)
VALUES ('111111111111111111111111',
        'With body',
        'With body',
        'With body',
        NULL,
        '{}',
        '{}');
