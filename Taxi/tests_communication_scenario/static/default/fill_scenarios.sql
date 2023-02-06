INSERT INTO scenarios (id, name, data, created)
VALUES (1, 'scenario',
        '{
          "steps": [
            {
              "name": "push",
              "channel": {
                "type": "go/push/user",
                "settings": {
                  "push_go": {
                    "ttl": 30
                  }
                }
              },
              "payload": { "payload" : { "id" : "123" } },
              "followers": []
            },
            {
              "name": "reserve_push",
              "channel": {
                "type": "go/push/user",
                "settings": {
                  "push_go": {
                    "ttl": 30
                  }
                }
              },
              "payload": { "payload": {} },
              "followers": []
            },
            {
              "name": "sms",
              "channel": {
                "type": "go/sms/user",
                "settings": {
                  "sms": {
                    "ttl": 30
                  }
                }
              },
              "payload": {},
              "followers": []
            }
          ],
          "initial_steps": [
            { "step":"push" }, { "step": "sms" }, { "step": "reserve_push" }
          ]
        }', NOW());

INSERT INTO launches (launch_id, parameters, recipient, channels, start_parameters)
VALUES ('a0eebc999c0b4ef8bb6d6bb9bd380a11',
        '{"push": { "payload": {"payload": {}}, "is_followers_enabled": [] },
        "sms": { "payload": {"text": "Hello!"}, "is_followers_enabled": [] },
        "reserve_push": { "payload": {"payload": {}}, "is_followers_enabled": [] }}',
        '{ "contact_info": [{ "type": "go_user_id", "value" : "1" }] }', '{ "push": {"channel_type": "push_go",
        "intent": "Test"}, "sms": {"channel_type": "sms", "intent": "Test"}, "reserve_push": {"channel_type": "push_go",
        "intent": "Test"} }', '{}');
