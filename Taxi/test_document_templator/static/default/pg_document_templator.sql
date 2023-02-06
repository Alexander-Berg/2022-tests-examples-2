INSERT INTO "document_templator"."requests" (id,
                                             name,
                                             description,
                                             endpoint_name,
                                             body_schema,
                                             response_schema,
                                             query)
VALUES ('5ff4901c583745e089e55bd1',
        'Tariff name',
        'Tariff description',
        'Tariff',
        '{}',
        '{}',
        '{"q1","q2"}'),
       ('5ff4901c583745e089e55bd2',
        'Text',
        'Text',
        'Text',
        NULL,
        '{}',
        NULL),
       ('5ff4901c583745e089e55bd3',
        'Surge',
        'Surge description',
        'Surge',
        NULL,
        '{}',
        NULL),
       ('5d275bc3eb584657ebbf24b2',
        'Second tariff',
        'Second tariff',
        'Second tariff',
        NULL,
        '{}',
        NULL),
       ('123451234512345123451234',
        'Double number',
        'Double number',
        'Double number',
        NULL,
        '{}',
        '{}'),
       ('111111111111111111111111',
        'With body',
        'With body',
        'With body',
        NULL,
        '{}',
        '{}');

INSERT INTO "document_templator"."template_groups" (id,
                                                    name,
                                                    description,
                                                    parent_id)
VALUES ('000000000000000000000001',
        'main',
        NULL,
        NULL),
       ('000000000000000000000002',
        'sub main',
        'description sub main',
        '000000000000000000000001');

INSERT INTO "document_templator"."dynamic_document_groups" (id,
                                                            name,
                                                            description,
                                                            parent_id)
VALUES ('000000000000000000000001',
        'main',
        NULL,
        NULL);


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
VALUES ('5ff4901c583745e089e55ba4',
        0,
        NULL,
        NULL,
        'empty template',
        'empty template',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[]'::JSONB,
        '[]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('111111111111111111111111',
        0,
        NULL,
        NULL,
        '111111111111111111111111',
        '111111111111111111111111',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[]'::JSONB,
        '[]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('5ff4901c583745e089e55be1',
        1,
        '{"5ff4901c583745e089e55be2","5ff4901c583745e089e55ba4"}',
        NULL,
        'test',
        'some text',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "description": "template parameter1 description",
            "name": "template parameter1",
            "schema": {
              "properties": {
                "v1": {
                  "type": "string"
                },
                "v2": {
                  "type": "number"
                },
                "v3": {
                  "type": "boolean"
                },
                "v4": {
                  "properties": {
                    "v4v1": {
                      "items": {
                        "type": "number"
                      },
                      "type": "array"
                    },
                    "v4v2": {
                      "type": "number"
                    }
                  },
                  "type": "object"
                }
              },
              "type": "object"
            },
            "type": "object"
          },
          {
            "name": "template parameter2",
            "schema": {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            "type": "array"
          },
          {
            "name": "template parameter3",
            "type": "string"
          },
          {
            "name": "template parameter4",
            "type": "number"
          },
          {
            "name": "template parameter5",
            "type": "boolean"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "template parameter1"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "template parameter2"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "template parameter3"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "template parameter4"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "template parameter5"
          }
        ]'::JSONB,
        '[
          {
            "description": "item1 description",
            "items": [
              {
                "description": "item1 description",
                "params": [
                  {
                    "data_usage": "OWN_DATA",
                    "name": "subitem1 parameter1",
                    "type": "array",
                    "value": [
                      1,
                      2
                    ]
                  }
                ],
                "persistent_id": "5ff4901c583745e089e55ba3",
                "properties": {},
                "template_id": "5ff4901c583745e089e55ba4"
              },
              {
                "content": "some content",
                "description": "item2 description",
                "persistent_id": "5ff4901c583745e089e55ba4"
              }
            ],
            "params": [
              {
                "data_usage": "OWN_DATA",
                "description": "contains array OWN_DATA",
                "name": "own array parameter",
                "type": "array",
                "value": [
                  "mama",
                  "papa"
                ]
              },
              {
                "data_usage": "OWN_DATA",
                "description": "contains string OWN_DATA",
                "name": "own string parameter",
                "type": "string",
                "value": "some string"
              },
              {
                "data_usage": "OWN_DATA",
                "description": "contains number OWN_DATA",
                "name": "own number parameter",
                "type": "number",
                "value": 0
              },
              {
                "data_usage": "OWN_DATA",
                "description": "contains boolean OWN_DATA",
                "name": "own boolean parameter",
                "type": "boolean",
                "value": false
              },
              {
                "data_usage": "OWN_DATA",
                "description": "contains object OWN_DATA",
                "name": "own object parameter",
                "type": "object",
                "value": {
                  "own_obj_data": 100
                }
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "description": "contains array PARENT_TEMPLATE_DATA",
                "name": "parent template array parameter",
                "type": "array",
                "value": "template parameter2"
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "description": "contains string PARENT_TEMPLATE_DATA",
                "name": "parent template string parameter",
                "type": "string",
                "value": "template parameter3"
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "description": "contains number PARENT_TEMPLATE_DATA",
                "name": "parent template number parameter",
                "type": "number",
                "value": "template parameter4"
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "description": "contains boolean PARENT_TEMPLATE_DATA",
                "name": "parent template boolean parameter",
                "type": "boolean",
                "value": "template parameter5"
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "description": "contains object PARENT_TEMPLATE_DATA",
                "name": "parent template object parameter",
                "type": "object",
                "value": "template parameter1.v4"
              },
              {
                "data_usage": "SERVER_DATA",
                "description": "contains array SERVER_DATA",
                "name": "server array parameter",
                "type": "array",
                "value": "req2.arr"
              },
              {
                "data_usage": "SERVER_DATA",
                "description": "contains string SERVER_DATA",
                "name": "server string parameter",
                "type": "string",
                "value": "req1.r1"
              },
              {
                "data_usage": "SERVER_DATA",
                "description": "contains number SERVER_DATA",
                "name": "server number parameter",
                "type": "number",
                "value": "req3.num"
              },
              {
                "data_usage": "SERVER_DATA",
                "description": "contains boolean SERVER_DATA",
                "name": "server boolean parameter",
                "type": "boolean",
                "value": "req3.bool"
              },
              {
                "data_usage": "SERVER_DATA",
                "description": "contains object SERVER_DATA",
                "name": "server object parameter",
                "type": "object",
                "value": "req1"
              }
            ],
            "persistent_id": "5ff4901c583745e089e55ba1",
            "properties": {},
            "requests_params": [
              {
                "id": "5ff4901c583745e089e55bd3",
                "name": "req"
              }
            ],
            "template_id": "5ff4901c583745e089e55be2"
          },
          {
            "content": "<p>Some content</p>",
            "persistent_id": "5ff4901c583745e089e55ba2"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba1",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba2",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "req1",
            "request_id": "5ff4901c583745e089e55bd1"
          },
          {
            "name": "req2",
            "request_id": "5ff4901c583745e089e55bd2"
          },
          {
            "name": "req3",
            "request_id": "5ff4901c583745e089e55bd3"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "req1"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "req2"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "req3"
          }
        ]'::JSONB,
        NULL),
       ('5ff4901c583745e089e55be2',
        0,
        '{}',
        NULL,
        'text',
        'some',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "own array parameter",
            "schema": {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            "type": "array"
          },
          {
            "name": "own string parameter",
            "type": "string"
          },
          {
            "name": "own number parameter",
            "type": "number"
          },
          {
            "name": "own object parameter",
            "schema": {
              "properties": {
                "own_obj_data": {
                  "type": "number"
                }
              },
              "type": "object"
            },
            "type": "object"
          },
          {
            "name": "parent template array parameter",
            "schema": {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            "type": "array"
          },
          {
            "name": "parent template string parameter",
            "type": "string"
          },
          {
            "name": "parent template number parameter",
            "type": "number"
          },
          {
            "name": "parent template object parameter",
            "schema": {
              "properties": {
                "v4v1": {
                  "items": {
                    "type": "number"
                  },
                  "type": "array"
                },
                "v4v2": {
                  "type": "number"
                }
              },
              "type": "object"
            },
            "type": "object"
          },
          {
            "name": "server array parameter",
            "schema": {
              "type": "array"
            },
            "type": "array"
          },
          {
            "name": "server string parameter",
            "type": "string"
          },
          {
            "name": "server number parameter",
            "type": "number"
          },
          {
            "name": "server object parameter",
            "schema": {
              "properties": {
                "r1": {
                  "type": "string"
                }
              },
              "type": "object"
            },
            "type": "object"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "own array parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "own string parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "own number parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "own object parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "parent template array parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "parent template string parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "parent template number parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "parent template object parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "server array parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "server string parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "server number parameter"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "server object parameter"
          }
        ]'::JSONB,
        '[
          {
            "content": "<p>OWN_DATA string [<span data-variable=\"own string parameter\"></span>]</p>\n<p>OWN_DATA number\n<span data-variable=\"own number parameter\"></span>\n</p>\n<p>OWN_DATA boolean\n<span data-variable=\"own boolean parameter\"></span>\n</p>\n<p>OWN_DATA object: <span data-variable=\"own object parameter.own_obj_data\"></span></p>\n<p>PARENT_TEMPLATE_DATA string: <span data-variable=\"parent template string parameter\"></span></p>\n<p>PARENT_TEMPLATE_DATA number: <span data-variable=\"parent template number parameter\"></span></p>\n<p>PARENT_TEMPLATE_DATA boolean: <span data-variable=\"parent template boolean parameter\"></span></p>\n<p>PARENT_TEMPLATE_DATA object: <span data-variable=\"parent template object parameter.v4v2\"></span></p>\n<p>SERVER_DATA string: <span data-variable=\"server string parameter\"></span></p>\n<p>SERVER_DATA number: <span data-variable=\"server number parameter\"></span></p>\n<p>SERVER_DATA boolean: <span data-variable=\"server boolean parameter\"></span></p>\n<p>SERVER_DATA object: <span data-variable=\"server object parameter.r1\"></span></p>\n<p>SERVER_DATA string: <span data-variable=\"req.num\" data-request-id=\"5ff4901c583745e089e55bd3\"></span></p>",
            "persistent_id": "5ff4901c583745e089e55ba5"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba5",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "req",
            "request_id": "5ff4901c583745e089e55bd3"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "req"
          }
        ]'::JSONB,
        NULL),
       ('5ff4901c583745e089e55be3',
        0,
        '{}',
        NULL,
        'Rest',
        'frost',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[
          {
            "content": "",
            "persistent_id": "5ff4901c583745e089e55ba6"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba6",
            "version": 0
          }
        ]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('5ff4901c583745e089e55be4',
        0,
        '{"5ff4901c583745e089e55be3"}',
        NULL,
        'most',
        'rEsT cost',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[
          {
            "items": [
              {
                "persistent_id": "6ff4901c583745e089e55ba7",
                "template_id": "5ff4901c583745e089e55be3"
              }
            ],
            "persistent_id": "5ff4901c583745e089e55ba7"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba7",
            "version": 0
          }
        ]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('5ff4901c583745e089e55be5',
        0,
        '{}',
        NULL,
        'Tost',
        'post',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[]'::JSONB,
        '[]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('5d27219b73f3b64036c0a03a',
        0,
        '{}',
        NULL,
        'simple text',
        'simple text',
        NULL,
        NULL,
        'russhakirov',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "str",
            "schema": {
              "str": {
                "type": "string"
              }
            },
            "type": "string"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "str"
          }
        ]'::JSONB,
        '[
          {
            "content": "Simple text and resolved parent template parameter&nbsp;<span style=\"color: Coral;\" data-variable=\"str\"></span>",
            "persistent_id": "5ff4901c583745e089e55ba9"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55ba9",
            "version": 0
          }
        ]'::JSONB,
        NULL,
        NULL,
        NULL),
       ('5d275bee73f3b64037c2d1af',
        0,
        '{}',
        NULL,
        'simple request',
        'simple request',
        NULL,
        NULL,
        'russhakirov',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[
          {
            "content": "Activation zone&nbsp;<span data-request-id=\"5d275bc3eb584657ebbf24b2\" style=\"color: Coral;\" data-variable=\"tariff.activation_zone\"></span>",
            "persistent_id": "5ff4901c583745e089e55bb1"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55bb1",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "tariff",
            "request_id": "5d275bc3eb584657ebbf24b2"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "tariff"
          }
        ]'::JSONB,
        NULL),
       ('5d275bee73f3b64037c2d1a9',
        0,
        '{}',
        NULL,
        'template with embedded templates to content',
        'template with embedded templates to content',
        NULL,
        NULL,
        'russhakirov',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[
          {
            "content": "First item wth just text <strong>bold</strong>\n",
            "persistent_id": "5ff4901c583745e089e55bb2"
          },
          {
            "content": "Second item with variables Number -&nbsp;<span style=\"color: Coral;\" data-variable=\"number\"></span>, String - <span style=\"color: Coral;\" data-variable=\"string\"></span>, Object param - <span style=\"color: Coral;\" data-variable=\"obj.param1\"></span>\n",
            "persistent_id": "5ff4901c583745e089e55bb9"
          },
          {
            "content": "Third item with request variable&nbsp;<span data-request-id=\"5d275bc3eb584657ebbf24b2\" style=\"color: Coral;\" data-variable=\"tariff_request.activation_zone\"></span>\n",
            "persistent_id": "5ff4901c583745e089e55bb3"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55bb2",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55bb9",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "5ff4901c583745e089e55bb3",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "tariff_request",
            "request_id": "5d275bc3eb584657ebbf24b2"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "tariff_request"
          }
        ]'::JSONB,
        NULL),
       ('1ff4901c583745e089e55be0',
        0,
        NULL,
        NULL,
        'base',
        'base template',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "description": "base template parameter1 description",
            "name": "base template parameter1",
            "type": "string"
          },
          {
            "description": "base template parameter2 description",
            "name": "base template parameter2",
            "type": "string"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "base template parameter1"
          },
          {
            "enabled": false,
            "inherited": false,
            "name": "base template parameter2"
          }
        ]'::JSONB,
        '[
          {
            "content": "BASE ITEM1 <p>Base PARENT_DATA string [<span data-variable=\"base template parameter1\"></span>]</p>\n<p>Base SERVER_DATA string: <span data-variable=\"req1.num\" data-request-id=\"5ff4901c583745e089e55bd3\"></span></p>\n\n",
            "persistent_id": "1ff4901c583745e089e55ba1"
          },
          {
            "content": "BASE ITEM2 <p>Base PARENT_DATA string [<span data-variable=\"base template parameter2\"></span>]</p>\n<p>Base SERVER_DATA string: <span data-variable=\"req2.r1\" data-request-id=\"5ff4901c583745e089e55bd1\"></span></p>\n\n",
            "persistent_id": "1ff4901c583745e089e55ba2"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "1ff4901c583745e089e55ba1",
            "version": 0
          },
          {
            "enabled": false,
            "inherited": false,
            "persistent_id": "1ff4901c583745e089e55ba2",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "req1",
            "request_id": "5ff4901c583745e089e55bd3"
          },
          {
            "name": "req2",
            "request_id": "5ff4901c583745e089e55bd1"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "req1"
          },
          {
            "enabled": false,
            "inherited": false,
            "name": "req2"
          }
        ]'::JSONB,
        NULL),
       ('1ff4901c583745e089e55be1',
        0,
        '{"1ff4901c583745e089e55be0"}',
        '1ff4901c583745e089e55be0',
        'child1',
        'child1 template',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "description": "child1 template parameter1 description",
            "name": "child1 template parameter1",
            "type": "number"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "name": "base template parameter1"
          },
          {
            "enabled": false,
            "inherited": true,
            "name": "base template parameter2"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "child1 template parameter1"
          }
        ]'::JSONB,
        '[
          {
            "content": "CHILD1 ITEM3 <p>Child1 PARENT_DATA number [<span data-variable=\"child1 template parameter1\"></span>]</p>\n<p>Child1 SERVER_DATA string: <span data-variable=\"req3.home_zone\" data-request-id=\"5d275bc3eb584657ebbf24b2\"></span></p>\n\n",
            "persistent_id": "1ff4901c583745e089e55ba3"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba1",
            "version": 0
          },
          {
            "enabled": false,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba2",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "1ff4901c583745e089e55ba3",
            "version": 0
          }
        ]'::JSONB,
        '[
          {
            "name": "req3",
            "request_id": "5d275bc3eb584657ebbf24b2"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "name": "req1"
          },
          {
            "enabled": false,
            "inherited": true,
            "name": "req2"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "req3"
          }
        ]'::JSONB,
        NULL),
       ('1ff4901c583745e089e55be2',
        0,
        '{"1ff4901c583745e089e55be0"}',
        '1ff4901c583745e089e55be0',
        'child2',
        'child2 template',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[]'::JSONB,
        '[
          {
            "enabled": false,
            "inherited": true,
            "name": "base template parameter1"
          },
          {
            "enabled": true,
            "inherited": true,
            "name": "base template parameter2"
          }
        ]'::JSONB,
        '[
          {
            "content": "CHILD2 ITEM3 Some text\n\n",
            "persistent_id": "1ff4901c583745e089e55ba4"
          }
        ]'::JSONB,
        '[
          {
            "enabled": false,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba1",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba2",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "1ff4901c583745e089e55ba4",
            "version": 0
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[
          {
            "enabled": false,
            "inherited": true,
            "name": "req1"
          },
          {
            "enabled": true,
            "inherited": true,
            "name": "req2"
          }
        ]'::JSONB,
        NULL),
       ('1ff4901c583745e089e55be3',
        0,
        '{"1ff4901c583745e089e55be1"}',
        '1ff4901c583745e089e55be1',
        'child11',
        'child1s child1 template',
        NULL,
        NULL,
        'venimaster',
        '2018-07-01T00:00:00+03:00',
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "description": "child11 template parameter1 description",
            "name": "child11 template parameter1",
            "type": "string"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "name": "base template parameter1"
          },
          {
            "enabled": false,
            "inherited": true,
            "name": "base template parameter2"
          },
          {
            "enabled": true,
            "inherited": true,
            "name": "child1 template parameter1"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "child11 template parameter1"
          }
        ]'::JSONB,
        '[
          {
            "content": "CHILD11 ITEM3 <p>Child11 PARENT_DATA string [<span data-variable=\"child11 template parameter1\"></span>]</p>\n\n",
            "persistent_id": "1ff4901c583745e089e55ba5"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba1",
            "version": 0
          },
          {
            "enabled": false,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba2",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "1ff4901c583745e089e55ba5",
            "version": 0
          },
          {
            "enabled": true,
            "inherited": true,
            "persistent_id": "1ff4901c583745e089e55ba3",
            "version": 0
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": true,
            "name": "req1"
          },
          {
            "enabled": false,
            "inherited": true,
            "name": "req2"
          },
          {
            "enabled": true,
            "inherited": true,
            "name": "req3"
          }
        ]'::JSONB,
        NULL),
       ('000000000000000000000022',
        0,
        NULL,
        NULL,
        'iterable item',
        'iterable item',
        NULL,
        NULL,
        'yandex',
        '2018-07-01T00:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "description": "items",
            "name": "items",
            "type": "array"
          },
          {
            "description": "items-separator",
            "name": "items-separator",
            "type": "string"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "items"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "items-separator"
          }
        ]'::JSONB,
        '[
          {
            "custom_item_id": "ITERABLE",
            "description": "iterable",
            "items": [
              {
                "content": "<span data-variable=#item.value />",
                "persistent_id": "000000000000000000000023",
                "version": 1
              }
            ],
            "params": [
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "name": "#items",
                "type": "array",
                "value": "items"
              },
              {
                "data_usage": "PARENT_TEMPLATE_DATA",
                "name": "#items-separator",
                "type": "string",
                "value": "items-separator"
              }
            ],
            "persistent_id": "000000000000000000000022"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "000000000000000000000022",
            "version": 1
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB),
       ('000000000000000000000002',
        0,
        '{"000000000000000000000042"}',
        '000000000000000000000042',
        'has document',
        'has document',
        NULL,
        NULL,
        'yandex',
        '2018-07-01T00:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "param",
            "schema": {
              "type": "number"
            },
            "type": "number"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "param"
          }
        ]'::JSONB,
        '[
          {
            "content": "---<span data-enumerator=\"base\"/>---<span data-enumerator=\"sub_base\"/>; param=<span data-variable=\"param\"/>",
            "description": "test",
            "persistent_id": "999999999999999999999990"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "999999999999999999999990",
            "version": 1
          }
        ]'::JSONB,
        '[
          {
            "name": "request",
            "request_id": "5ff4901c583745e089e55bd3"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "request"
          }
        ]'::JSONB,
        '[
          {
            "formatter": {
              "code": "ARABIC_NUMBER",
              "start_symbol": "1"
            },
            "name": "base"
          },
          {
            "formatter": {
              "code": "ARABIC_NUMBER",
              "start_symbol": "1"
            },
            "name": "sub_base",
            "parent_name": "base"
          }
        ]'::JSONB),
       ('000000000000000000000042',
        0,
        NULL,
        NULL,
        'www document',
        'www document',
        NULL,
        NULL,
        'yandex',
        '2018-07-01T01:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        NULL,
        NULL,
        '[]'::JSONB,
        '[]'::JSONB,
        NULL,
        NULL,
        '[
          {
            "formatter": {
              "code": "ARABIC_NUMBER",
              "start_symbol": "1"
            },
            "name": "common"
          }
        ]'::JSONB),
       ('000000000000000000000001',
        0,
        NULL,
        NULL,
        'has no dependency',
        'has no dependency',
        NULL,
        NULL,
        'yandex',
        '2018-07-01T00:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        '[]'::JSONB,
        '[]'::JSONB,
        '[
          {
            "content": "---<span data-enumerator=\"base\"/>---<span data-enumerator=\"sub_base\"/>",
            "description": "with enumerators",
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
        '[]'::JSONB,
        '[]'::JSONB,
        '[
          {
            "formatter": {
              "code": "ARABIC_NUMBER",
              "start_symbol": "1"
            },
            "name": "base"
          },
          {
            "formatter": {
              "code": "ARABIC_NUMBER",
              "start_symbol": "1"
            },
            "name": "sub_base",
            "parent_name": "base"
          }
        ]'::JSONB),
       ('000000000000000000000003',
        1,
        NULL,
        NULL,
        'has group',
        'has group',
        '000000000000000000000001',
        NULL,
        'yandex',
        '2018-07-01T00:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB),
       ('000000000000000000000004',
        1,
        NULL,
        NULL,
        'has sub group',
        'has sub group',
        '000000000000000000000002',
        NULL,
        'yandex',
        '2018-07-01T00:00:00+03:00',
        'yandex',
        '2018-07-01T01:00:00+03:00',
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB),
       ('000000000000000000000008',
        0,
        NULL,
        NULL,
        'with string and number param',
        'with string and number param',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "number",
            "type": "number"
          },
          {
            "name": "string",
            "type": "string"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "number"
          },
          {
            "enabled": true,
            "inherited": false,
            "name": "string"
          }
        ]'::JSONB,
        '[
          {
            "content": "<span data-variable=\"number\"/>-<span data-variable=\"string\"/>",
            "description": "",
            "persistent_id": "999999999999999999999991"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "999999999999999999999991",
            "version": 1
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB),
       ('000000000000000000000009',
        0,
        NULL,
        NULL,
        'with array',
        'with array',
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
            "content": "<span data-variable=\"array\"/>",
            "description": "",
            "persistent_id": "999999999999999999999992"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "999999999999999999999992",
            "version": 1
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB),
       ('000000000000000000000010',
        0,
        NULL,
        NULL,
        'with object param',
        'with object param',
        NULL,
        NULL,
        'robot',
        '2018-07-01T00:00:00+03:00',
        'robot',
        '2018-07-01T01:00:00+03:00',
        '[
          {
            "name": "object",
            "type": "object"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "name": "object"
          }
        ]'::JSONB,
        '[
          {
            "content": "<span data-variable=\"object.key1\"/>-<span data-variable=\"object.key2\"/>",
            "description": "",
            "persistent_id": "999999999999999999999991"
          }
        ]'::JSONB,
        '[
          {
            "enabled": true,
            "inherited": false,
            "persistent_id": "999999999999999999999991",
            "version": 1
          }
        ]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB,
        '[]'::JSONB);

INSERT INTO "document_templator"."dynamic_documents" (created_by,
                                                      created_at,
                                                      description,
                                                      generated_text,
                                                      is_valid,
                                                      modified_by,
                                                      modified_at,
                                                      name,
                                                      params,
                                                      persistent_id,
                                                      version,
                                                      removed,
                                                      requests_params,
                                                      template_id,
                                                      group_id,
                                                      outdated_at)
VALUES ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'some text',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'test',
        '[
          {
            "name": "dynamic document parameter1",
            "value": "dynamic document parameter1 value"
          },
          {
            "name": "dynamic document parameter2",
            "value": 1
          }
        ]'::JSONB,
        '5ff4901c583745e089e55bf1',
        0,
        True,
        '[]',
        '5ff4901c583745e089e55be1',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'some text',
        'some generated text',
        True,
        'venimaster',
        '2018-07-01T01:00:00+03:00',
        'test',
        '[
          {
            "name": "template parameter1",
            "value": {
              "v1": "str1",
              "v2": 0,
              "v3": true,
              "v4": {
                "v4v1": [
                  0,
                  1,
                  2
                ],
                "v4v2": 42
              }
            }
          },
          {
            "name": "template parameter2",
            "value": [
              2,
              1,
              0
            ]
          },
          {
            "name": "template parameter3",
            "value": "some string"
          },
          {
            "name": "template parameter4",
            "value": 100500
          },
          {
            "name": "template parameter5",
            "value": true
          }
        ]'::JSONB,
        '5ff4901c583745e089e55bf1',
        1,
        False,
        '[
          {
            "body": {
              "a": {
                "b": [],
                "c": 1
              }
            },
            "id": "5ff4901c583745e089e55bd1",
            "name": "req1",
            "query": {
              "q1": 1,
              "q2": "string"
            },
            "substitutions": {
              "tariff": "econom",
              "zone": "moscow"
            }
          },
          {
            "id": "5ff4901c583745e089e55bd2",
            "name": "req2"
          },
          {
            "id": "5ff4901c583745e089e55bd3",
            "name": "req3"
          }
        ]'::JSONB,
        '5ff4901c583745e089e55be1',
        '000000000000000000000001',
        '2018-07-02T01:00:00+03:00'),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'some',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'text',
        '[]',
        '5ff4901c583745e089e55bf2',
        1,
        False,
        '[]',
        '5ff4901c583745e089e55be2',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'frost',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'Rest',
        '[]',
        '5ff4901c583745e089e55bf3',
        1,
        False,
        '[]',
        '5ff4901c583745e089e55be3',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'rEsT cost',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'most',
        '[]',
        '5ff4901c583745e089e55bf4',
        1,
        False,
        '[]',
        '5ff4901c583745e089e55be4',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'post',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'Tost',
        '[]',
        '5ff4901c583745e089e55bf5',
        1,
        False,
        '[]',
        '5ff4901c583745e089e55be5',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'deleted documment',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'Tost',
        '[]',
        '5ff4901c583745e089e55bf6',
        0,
        True,
        '[]',
        '5ff4901c583745e089e55be5',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'deleted documment',
        'some generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'Tost',
        '[]',
        '5ff4901c583745e089e55bf6',
        1,
        True,
        '[]',
        '5ff4901c583745e089e55be5',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'd',
        '',
        False,
        'venimaster',
        '2018-07-01T01:00:00+03:00',
        'n',
        '[]',
        '5ff4901c583745e089e55bf8',
        1,
        False,
        '[]',
        '5ff4901c583745e089e55be5',
        NULL,
        '2018-07-01T01:00:00+03:00'),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        'not valid data',
        False,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'n11',
        '[]',
        '1ff4901c583745e089e55bf0',
        1,
        False,
        '[]',
        '1ff4901c583745e089e55be3',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        'some text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'n11',
        '[]',
        '1ff4901c583745e089e55bf0',
        0,
        True,
        '[]',
        '1ff4901c583745e089e55be3',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        '',
        False,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'do not have not removed versions',
        '[]',
        '000009999988888777776666',
        0,
        True,
        '[]',
        '111111111111111111111111',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        'invalid data',
        False,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'two last version is not valid',
        '[]',
        '000009999988888777771111',
        0,
        True,
        '[]',
        '111111111111111111111111',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        'invalid data',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'two last version is not valid',
        '[]',
        '000009999988888777771111',
        1,
        True,
        '[]',
        '111111111111111111111111',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        'generated text',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'two last version is not valid',
        '[]',
        '000009999988888777771111',
        2,
        True,
        '[]',
        '111111111111111111111111',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        '',
        False,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'two last version is not valid',
        '[]',
        '000009999988888777771111',
        3,
        True,
        '[]',
        '111111111111111111111111',
        NULL,
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'generated based on child11 template',
        '',
        False,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'two last version is not valid',
        '[]',
        '000009999988888777771111',
        4,
        False,
        '[]',
        '111111111111111111111111',
        '000000000000000000000001',
        NULL),
       ('venimaster',
        '2018-07-01T00:00:00+03:00',
        'just document',
        '---1---1.1; param=1',
        True,
        'russhakirov',
        '2018-07-01T01:00:00+03:00',
        'just document',
        '[
          {
            "name": "param",
            "value": 1
          }
        ]'::JSONB,
        '000009999988888777772222',
        1,
        False,
        '[
          {
            "id": "5ff4901c583745e089e55bd3",
            "name": "request"
          }
        ]'::JSONB,
        '000000000000000000000002',
        NULL,
        NULL);
