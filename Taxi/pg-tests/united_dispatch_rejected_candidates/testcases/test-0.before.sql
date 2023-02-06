-- 2 records: 
--   1 - old (remove)
--   2 - fresh (skip)

INSERT INTO united_dispatch.rejected_candidates (
        delivery_id, candidate_id, rejections, created_ts, updated_ts) 
VALUES (
        '1', '1', 1, '2021-11-17 19:59:01', '2021-11-17 19:59:02'
        ),
        (
        '2', '2', 1, '2021-11-18 20:00:01', '2021-11-18 20:00:02'
        );
