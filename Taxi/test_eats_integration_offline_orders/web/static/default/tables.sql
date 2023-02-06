insert into tables
(
    uuid,
    table_pos_id,
    table_pos_name,
    place_id,
    table_ya_id,
    deleted_at
)
values
('uuid__1', 'table_id__1', 'table_id__1', 'place_id__1', '1', NULL),
('uuid__2', 'table_id__2', 'table_id__2', 'place_id__2', '2', NULL),
('uuid__3', 'table_id__3', 'table_id__3', 'place_id__3', '3', NULL),
('uuid__4', 'table_id__4', '', 'place_id__3', '4', NULL),
('uuid__5', 'table_id__5', NULL, 'place_id__3', '5', NULL),
('uuid__6', 'table_id__6', NULL, 'place_id__3', '6', NOW()),
('uuid__7', 'table_id__7', 'table_id__7', 'place_id__4', '7', NULL)
;
