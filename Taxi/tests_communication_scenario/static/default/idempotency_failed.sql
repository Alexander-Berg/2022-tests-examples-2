INSERT INTO
    idempotency_tokens
    (request_type, token, expire_at, status, handler_data)
VALUES
    ('/v1/start:push_sms:', '123', (NOW() + INTERVAL '1 hour'), 'failed', '{"launch_id": "c8dd3f6d80d84edba0eb228aa3a744e0"}')
 
