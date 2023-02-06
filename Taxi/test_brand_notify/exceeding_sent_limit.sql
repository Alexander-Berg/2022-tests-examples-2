insert into order_history_notifications (
    order_nr,
    courier_id,
    retries,
    created_at
)
values
('correct order', '2', 5, now() - interval '50 minutes'),
('11', '1', 5, now()),
('12', '3', 2, now() - interval '30 minutes'),
('correct order', '1', 5, now()),
('13', '2', 2, now() - interval '50 minutes');
