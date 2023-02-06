INSERT INTO launches (launch_id, parameters, recipient, channels, created)
VALUES ('a0eebc999c0b4ef8bb6d6bb9bd380a11',
        '{"push": { "payload": {"payload": {}}, "is_followers_enabled": [] },
        "sms": { "payload": {"text": "Hello!"}, "is_followers_enabled": [] },
        "reserve_push": { "payload": {"payload": {}}, "is_followers_enabled": [] }}',
        '{ "contact_info": [{ "type": "go_user_id", "value" : "1" }] }', '{ "push": {"channel_type": "push_go",
        "intent": "Test"}, "sms": {"channel_type": "sms", "intent": "Test"}, "reserve_push": {"channel_type": "push_go",
        "intent": "Test"} }', (NOW() - INTERVAL '1 hour'));
