insert into restaurants
(place_id, slug, name, pos_type, logo_link, description, enabled, tips_link_fallback, billing_client_id, geo_point, region_id, personal_tin_id, last_time_table_check)
values
('place_id__1', 'place_id__1_slug', 'Самый тестовый ресторан', 'iiko', '135516/147734d81d1de576476c6a217679e1c29f83eeb7', NULL, TRUE, 'some_tips_link', 'billing_client_id__1', '(39.022872,45.056503)'::POINT, 13, 'personal_tin_id__1', '2022-05-16T10:00:00+00:00')
;

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
