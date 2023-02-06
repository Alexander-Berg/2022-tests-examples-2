INSERT INTO hiring_candidates.communication_yt_tables(
    table_path,
    created_ts
)
VALUES (
        'test_path',
        '2020-01-01'::TIMESTAMP
);


INSERT INTO hiring_candidates.communication_drivers(
    created_dttm,
    driver_id,
    is_rent,
    table_path,
    personal_phone_id,
    name,
    unique_driver_id,
    driver_license_personal_id,
    comm_type,
    city,
    created_row_ts
    ) VALUES (
    '2020-08-01',
    'driver_id',
    'true',
    'test_path',
    'f5b6a9399d624084ae0ff73e6f67174f',
    'Ivan',
    'unique_driver_id',
    'bd4c88e3e36b4cc58f993c2d19794dca',
    'text',
    'moscow',
    '2020-08-01'::TIMESTAMP
),
(
    '2020-08-01',
    'driver_id_1',
    'false',
    'test_path',
    '2aef6af8cc8246af9253fd08dcedba87',
    'Vasya',
    'unique_driver_id',
    'b096c787cc744c33bca703990fef384b',
    'text',
    'moscow',
    '2020-08-01'::TIMESTAMP
),
(
    '2020-08-01',
    'driver_id_2',
    'false',
    'test_path',
    '6ba83c0cb6c8451a9f30759534e03aab',
    'Kirill',
    'unique_driver_id',
    '260c2e98b6514594bc988171ba2b16f7',
    'text',
    'moscow',
    '2020-08-01'::TIMESTAMP
);

INSERT INTO hiring_candidates.candidates(
    id,
    personal_phone_id
) VALUES (
    '0000',
    'ab5d889aab6d448091766a7649c604ce'
),
(
    '0001',
    'c6f13636554a492cb284e2b40c6fc0bb'
);

INSERT INTO hiring_candidates.leads(
    lead_id,
    candidate_id,
    account_id,
    created_ts,
    is_rent,
    personal_license_id,
    license_country,
    service,
    workflow_type,
    first_name
) VALUES (
    'akjhsdf123',
    '0000',
    'test_acc',
    '2020-09-14T13:00:00'::TIMESTAMP,
    FALSE,
    '37b48d6efd784ba4acc8ad33fc0bf218',
    'RUS',
    'taxi',
    'NotLeadSale',
    'Kirk'
),
(
    'akjhsdf124',
    '0001',
    'test_acc',
    '2020-09-14T13:00:00'::TIMESTAMP,
    TRUE,
    '84e68ba6534e49e2893151194a8b909b',
    'RUS',
    'taxi',
    'LeadSale',
    'Ivan'
);
