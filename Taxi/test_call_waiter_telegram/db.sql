insert into telegram_chats
(
    chat_id,
    chat_type,
    place_id
)
values
(1000000, 'group', 'place_id__1')
;

insert into pos_tokens
(
    pos_id,
    place_id,
    token
)
values
('pos_id__1', 'place_id__1', '')
;

insert into tables
(
    uuid,
    table_pos_id,
    place_id
)
values
('uuid__1', 'table_id__1', 'place_id__1')
;
