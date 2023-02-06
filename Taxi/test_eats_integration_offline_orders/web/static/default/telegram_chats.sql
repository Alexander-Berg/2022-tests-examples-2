INSERT INTO telegram_chats (
    place_id, chat_id, chat_type, disabled, deleted_at
)
VALUES
('place_id__1', 100500, 'group', false, NULL),
('place_id__2', 1234567890, 'group', false, NULL),
('place_id__2', -888888888, 'group', true, NULL),
('place_id__2', 19921031, 'group', false, NULL),
('place_id__2', 987654321, 'manager', false, '2022-01-01 12:00')
;
