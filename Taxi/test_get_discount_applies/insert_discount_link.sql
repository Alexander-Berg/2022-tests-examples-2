INSERT INTO corp_discounts.discount_links
(
    discount_id,
    client_id,
    valid_since,
    valid_until,
    activated_at
)
VALUES
-- insert absurdly large interval
(
    1, 'client_id_1', '2021-08-17T23:54:00+00:00', '2031-08-17T23:54:00+00:00', '2021-10-01T00:00:00+00:00'
)
