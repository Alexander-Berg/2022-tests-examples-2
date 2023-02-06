--!syntax_v1

UPSERT INTO `main/request_compilations/cursor_with_filters` (
    created_at,
    request_id,
    delivery_date,
    request_status,
    delivery_policy,
    employer_code,
    request_code,
    operator_id,
    recipient_phone_pd_id
) VALUES
(CAST(1743399569000000 AS Timestamp), '13aad1ae-c205-42e8-94e1-e7c96728d738', 
    CAST(1743399579000000 AS Timestamp), "canceled", "min_by_request", "first_employer", "request_code1", "strizh", "123456789abc"),
(CAST(1742738350000000 AS Timestamp), 'aadc50f7-5654-4f38-a669-de2aee65aeac', 
    CAST(1742838350000000 AS Timestamp), "processing", "min_by_request", "fourth_employer", "request_code4", "drozd", "one_two"),
(CAST(1770766632000000 AS Timestamp), '288affa0-50e8-458e-8ab7-5bdb8938de7a', 
    CAST(1770866632000000 AS Timestamp), "canceled", "min_by_request", "first_employer", "request_code6", "market", "some_id"),
(CAST(1772017115000000 AS Timestamp), '5d04acd2-aee3-4058-a194-57b6ddc635f5', 
    CAST(1772017125000000 AS Timestamp), "processing", "min_by_request", "second_employer", "request_code7", "strizh", "124567abc"),
(CAST(1770148072000000 AS Timestamp), 'b90b5b11-2b83-40fc-9920-957f43e602b6', 
    CAST(1770966632000000 AS Timestamp), "processing", "min_by_request", "fourth_employer", "request_code10", "unknown", "this_pd_id"),
(CAST(1770090329000000 AS Timestamp), '6d2b13a2-f55b-4063-a269-d91d545508ae', 
    CAST(1770090429000000 AS Timestamp), "finished", "another_policy", "third_employer", "request_code11", "drozd", "some_pd_id");
