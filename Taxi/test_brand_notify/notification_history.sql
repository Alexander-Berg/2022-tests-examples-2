insert into order_history_notifications (
    order_nr,
    courier_id,
    created_at
)
values
('correct order', '2', now()),
('11', '3', now()),
('12', '2', now()),
('correct order', '1', now() - interval '30 minutes'),
('13', '2', now());
