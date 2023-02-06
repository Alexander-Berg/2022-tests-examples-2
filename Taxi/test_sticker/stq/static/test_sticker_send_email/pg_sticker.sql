INSERT INTO sticker.mail_queue (
    id,
    body,
    idempotence_token,
    recipient,
    status,
    fail_count,
    retry_time,
    via_sender,
    sender_account,
    sender_campaign_slug,
    sender_args,
    sender_headers,
    from_name,
    from_email
)
VALUES
(
    1,
    '',
    '1',
    '1',
    'SCHEDULED',
    0,
    NULL,
    TRUE,
    'taxi',
    '8M6X0E93-W5O',
    '{"html_body": ""}'::JSONB,
    '{"X-Yandex-Hint": "label=SystMetkaSO:taxi"}'::JSONB,
    'Яндекс Go',
    'no-reply@taxi.yandex.ru'
),
(
    2,
    '',
    '2',
    '1',
    'PROCESSING',
    0,
    NULL,
    TRUE,
    'taxi',
    '8M6X0E93-W5O',
    '{"html_body": ""}'::JSONB,
    '{"X-Yandex-Hint": "label=SystMetkaSO:taxi"}'::JSONB,
    'Яндекс Go',
    'no-reply@taxi.yandex.ru'
),
(
    3,
    '',
    '3',
    '2_with_attachment',
    'TO_RETRY',
    1,
    '2020-09-17 11:50',
    TRUE,
    'taxi',
    '8M6X0E93-W5O',
    '{"html_body": ""}'::JSONB,
    '{"X-Yandex-Hint": "label=SystMetkaSO:taxi"}'::JSONB,
    'Яндекс Go',
    'no-reply@taxi.yandex.ru'
),
(
    4,
    '',
    '4',
    '3_fail',
    'TO_RETRY',
    9,
    '2020-09-17 11:50',
    TRUE,
    'taxi',
    '8M6X0E93-W5O',
    '{"html_body": ""}'::JSONB,
    '{"X-Yandex-Hint": "label=SystMetkaSO:taxi"}'::JSONB,
    'Яндекс Go',
    'no-reply@taxi.yandex.ru'
),
(
    5,
    '',
    '5',
    '3_fail',
    'PENDING',
    0,
    '2020-09-17 11:50',
    TRUE,
    'taxi',
    '8M6X0E93-W5O',
    '{"html_body": ""}'::JSONB,
    '{"X-Yandex-Hint": "label=SystMetkaSO:taxi"}'::JSONB,
    'Яндекс Go',
    'no-reply@taxi.yandex.ru'
)
;

INSERT INTO sticker.attachment (
     idempotence_token,
     recipient,
     body,
     content_type,
     file_name
)
VALUES
(
    '3',
    '2_with_attachment',
    'test',
    'application/pdf',
    'some.pdf'
)
;
