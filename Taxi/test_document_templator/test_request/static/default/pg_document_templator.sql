INSERT INTO "document_templator"."requests" (
    id,
    name,
    description,
    endpoint_name,
    body_schema,
    response_schema,
    query
)
VALUES ('5ff4901c583745e089e55bd1',
        'Tariff name',
        'Tariff description',
        'Tariff',
        '{
          "properties": {
            "a": {
              "properties": {
                "b": {
                  "type": "array"
                },
                "c": {
                  "type": "number"
                }
              },
              "type": "object"
            }
          },
          "type": "object"
        }',
        '{
          "properties": {
            "r1": {
              "type": "string"
            }
          },
          "type": "object"
        }',
        '{"q1","q2"}'),
       ('5ff4901c583745e089e55bd3',
        'Surge',
        'Surge description',
        'Surge',
        NULL,
        '{
          "properties": {
            "num": {
              "type": "number"
            }
          },
          "type": "object"
        }',
        NULL);
