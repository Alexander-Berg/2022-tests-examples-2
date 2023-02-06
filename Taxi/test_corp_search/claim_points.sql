INSERT INTO cargo_claims.claim_points (id, claim_id, point_id, type, visit_order)
VALUES
    (11, 1, 101, 'source', 1),
    (12, 2, 102, 'destination', 2),
    (13, 3, 103, 'source', 1),
    (14, 4, 104, 'source', 1),
    (15, 4, 105, 'destination', 2),
    (16, 1, 106, 'destination', 2),
-- multipoints expects source and destination exists
    (17, 2, 101, 'source', 1),
    (18, 3, 101, 'destination', 2),
-- multipoints should not lead to crash on search/v1  
    (19, 3, 103, 'destination', 3),
    (20, 3, 104, 'destination', 4);
