insert into eats_nomenclature_collector.place_tasks_last_status_history(
    id,
    place_id,
    task_type,
    status,
    status_or_text_changed_at,
    updated_at
)
values (1, '1', 'nomenclature', 'processed', now() - interval '2 hours', now() - interval '2 hours'),
       (2, '1', 'price', 'processed', now() - interval '2 hours', now() - interval '2 hours'),
       (3, '1', 'stock', 'processed', now(), now()),
       (4, '1', 'availability', 'processed', now(), now());
