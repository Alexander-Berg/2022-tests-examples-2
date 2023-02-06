-- today: 2020-04-21

INSERT INTO delivery.avito_subscription (item_id, vas_package_id, expire_date, applied_at)
 VALUES
        (7, 'pushup', '2020-04-20', '2020-04-13'), -- positive: expired
        (8, 'pushup', '2020-04-23', '2020-04-21'),         -- positive: active, but applied today
                                                          -- (could be other applications at the same day)
        (9, 'pushup', '2020-04-22', '2020-04-20')        -- negative: active, applied on the previous day
