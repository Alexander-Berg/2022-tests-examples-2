DELETE FROM corp_support_chat.request;

INSERT INTO corp_support_chat.request
(
    sf_id,
    yandex_chat_id,
    last_message_time,
    status
) VALUES
(
    '1',
    '1',
    '2022-6-25 00:00:00',
    'close'
),(
    '2',
    '2',
    now() - interval '20 minutes',
    'open'
),(
    '3',
    '3',
    now(),
    'open'
),(
    '4',
    '4',
    now() - interval '3 hours',
    'open'
),(
    '5',
    '5',
    now(),
    'pause'
),(
    '6',
    '6',
    now(),
    'close'
),(
    '7',
    '7',
    '2022-6-27 00:00:00',
    'pause'
)
