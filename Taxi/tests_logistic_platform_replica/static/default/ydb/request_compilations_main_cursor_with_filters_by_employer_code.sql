--!syntax_v1

UPSERT INTO `main/request_compilations/cursor_with_filters_by_employer_code` (
    employer_code,
    created_at,
    request_id,
    delivery_date,
    request_status,
    delivery_policy,
    operator_id,
    recipient_phone_pd_id
) VALUES
("first_employer", CAST(1643399569000000 AS Timestamp), '13aad1ae-c205-42e8-94e1-e7c96728d738', 
    CAST(1643399579000000 AS Timestamp), "canceled", "min_by_request", "strizh", "123456789abc"),
("second_employer", CAST(1641694841000000 AS Timestamp), '07243441-785b-4a70-a2c2-bf48348f4225', 
    CAST(1641694862000000 AS Timestamp), "unknown", "unknown", "lavka", "qwerty"),
("third_employer", CAST(1641490467000000 AS Timestamp), '2d6fb2df-15b9-4855-9cc1-e51f5f1bc674', 
    CAST(1641500467000000 AS Timestamp), "processing", "interval_with_fees", "strizh", "some_pd_id"),
("third_employer", CAST(1641966527000000 AS Timestamp), '3121c950-1024-4be1-9ba5-33e6dae2da4a', 
    CAST(1641966528000000 AS Timestamp), "canceled", "interval_with_fees", "unknown", "qwerty"),
("fourth_employer", CAST(1642738350000000 AS Timestamp), 'aadc50f7-5654-4f38-a669-de2aee65aeac', 
    CAST(1642838350000000 AS Timestamp), "processing", "min_by_request", "drozd", "one_two"),
("first_employer", CAST(1671161946000000 AS Timestamp), '09c7720b-8e6c-4d30-bd73-5d52916be754', 
    CAST(1681161946000000 AS Timestamp), "finished", "unknown", "unknown", "124567abc"),
("first_employer", CAST(1670766632000000 AS Timestamp), '288affa0-50e8-458e-8ab7-5bdb8938de7a', 
    CAST(1670866632000000 AS Timestamp), "canceled", "min_by_request", "market", "some_id"),
("second_employer", CAST(1672017115000000 AS Timestamp), '5d04acd2-aee3-4058-a194-57b6ddc635f5', 
    CAST(1672017125000000 AS Timestamp), "processing", "min_by_request", "strizh", "124567abc"),
("first_employer", CAST(1670018124000000 AS Timestamp), 'd81dec52-83e9-4175-93bb-0e913d6afbb9', 
    CAST(1680018124000000 AS Timestamp), "processing", "interval_with_fees", "lavka", "qwerty"),
("second_employer", CAST(1670765326000000 AS Timestamp), '1717dcb9-3767-4232-ac04-43b832006edd', 
    CAST(1670865326000000 AS Timestamp), "processing", "interval_with_fees", "some_operator", "this_pd_id"),
("fourth_employer", CAST(1670148072000000 AS Timestamp), 'b90b5b11-2b83-40fc-9920-957f43e602b6', 
    CAST(1670966632000000 AS Timestamp), "processing", "min_by_request", "unknown", "this_pd_id"),
("third_employer", CAST(1670090329000000 AS Timestamp), '6d2b13a2-f55b-4063-a269-d91d545508ae', 
    CAST(1670090429000000 AS Timestamp), "finished", "another_policy", "drozd", "some_pd_id");
