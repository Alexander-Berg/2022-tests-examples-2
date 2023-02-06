INSERT INTO price_modifications.rules (
     rule_id, name,
     source_code,
     policy, author,
     approvals_id, updated,
     pmv_task_id, deleted, ast
) VALUES (
        95, 'trip_depended',
        'let meta = {metadata= ["answer": 14]};
         return concat(ride.price*trip.time, meta);',
        'both_side', 'me',
        77777, '2020-01-10 18:23:11.5857+03',
        NULL, false, ''
), (
    2, 'paid_supply_x_100',
    'return ride.price*100;',
    'both_side', 'me',
    77778, '2020-01-10 18:23:11.5857+03',
    NULL, false, ''
);
