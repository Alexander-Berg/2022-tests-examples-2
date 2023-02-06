-- 2 records: 
--   1 - old (remove)
--   2 - fresh (skip)

INSERT INTO united_dispatch.frozen_candidates (
        candidate_id, waybill_id, expiration_ts, created_ts) 
VALUES (
        '1', '1', '2022-06-10T09:59:00+00', '2022-06-10T00:00:00+00'
        ),
        (
        '2', '2', '2022-06-10T10:00:10+00', '2022-06-10T00:00:00+00'
        );
