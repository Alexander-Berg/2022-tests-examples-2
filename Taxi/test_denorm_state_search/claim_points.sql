INSERT INTO cargo_claims.claim_points (id, claim_id, point_id, type, visit_order, claim_uuid)
VALUES
    (11, 1, 101, 'source', 1, 'b04a64bb1d0147258337412c01176fa1'),
    (12, 2, 102, 'destination', 2, 'b04a64bb1d0147258337412c01176fa2'),
    (13, 3, 103, 'source', 1, 'b04a64bb1d0147258337412c01176fa3'),
    (14, 4, 104, 'source', 1, 'b04a64bb1d0147258337412c01176fa4'),
    (15, 4, 105, 'destination', 2, 'b04a64bb1d0147258337412c01176fa4'),
    (16, 1, 106, 'destination', 2, 'b04a64bb1d0147258337412c01176fa1'),
-- multipoints expects source and destination exists
    (17, 2, 201, 'source', 1, 'b04a64bb1d0147258337412c01176fa2'),
    (18, 3, 301, 'destination', 2, 'b04a64bb1d0147258337412c01176fa3'),
-- multipoints should not lead to crash on search/v1  
    (19, 3, 203, 'destination', 3, 'b04a64bb1d0147258337412c01176fa3'),
    (20, 3, 204, 'destination', 4, 'b04a64bb1d0147258337412c01176fa3');
