INSERT INTO callcenter_stats.call_history
(id, call_id, queue, queued_at, answered_at, completed_at, created_at, endreason, direction)
VALUES
    ('51', '51', 'queue3', '2020-06-22T08:04:55.00Z', '2020-06-22T08:04:56.00Z', '2020-06-22T08:04:57.00Z', '2020-06-22T08:04:59.00Z', 'completed_by_caller', 'in'),  -- included w/o offset
    ('52', '52', 'queue3', '2020-06-22T08:04:43.00Z', '2020-06-22T08:04:45.00Z', '2020-06-22T08:04:47.00Z', '2020-06-22T08:04:49.00Z', 'completed_by_caller', 'in'),  -- included
    ('53', '53', 'queue3', '2020-06-22T08:03:51.00Z', '2020-06-22T08:03:54.00Z', '2020-06-22T08:03:57.00Z', '2020-06-22T08:03:59.00Z', 'completed_by_caller', null),  -- included w offset
    ('54', '54', 'queue3', '2020-06-22T08:04:43.00Z', '2020-06-22T08:04:45.00Z', '2020-06-22T08:04:47.00Z', '2020-06-22T08:04:49.00Z', 'completed_by_caller', 'out'), -- outgoing included
    ('55', '55', 'queue3', '2020-06-22T08:03:51.00Z', '2020-06-22T08:03:54.00Z', '2020-06-22T08:03:57.00Z', '2020-06-22T08:03:59.00Z', 'completed_by_caller', 'out')  -- outgoing w + w/o offset
