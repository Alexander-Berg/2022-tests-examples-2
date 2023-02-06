insert into callcenter_operators.shift_events (alias, description, properties, updated_at)
VALUES ('training', 'no matter train muscles or brain', '{"distribute_breaks_inside": true, "is_training": false}', '2020-11-16 14:10:00.0'),
       ('with_breaks', 'training with its own breaks inside', '{"distribute_breaks_inside": false, "is_training": true}',
        '2020-11-16 14:10:00.0');
