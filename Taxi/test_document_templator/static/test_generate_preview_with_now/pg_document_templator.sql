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
VALUES ('000000000000000000000001',
        0,
        NULL,
        NULL,
        'with now',
        'with now',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "array",
            "type": "array"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "array"
          }
        ]'::JSONB,
        '[
          {
            "content": "Date: <span data-variable=\"#now\"/>",
            "description": "with now",
            "persistent_id": "000000000000000000000001"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "000000000000000000000001",
            "version": 1
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB);
