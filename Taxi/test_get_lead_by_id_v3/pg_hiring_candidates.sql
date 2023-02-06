INSERT INTO hiring_candidates.assets (
    asset_id,
    lead_id,
    sts,
    plate_number,
    vin,
    brand,
    model,
    release_year,
    color,
    is_deleted
) VALUES (
    'maximal_lead_car',
    'PRS-LEAD-ID-MAX-131415',
    '101030405050234',
    'Т217НТ777',
    'XWB4A11BD8A139475',
    'Honda',
    'Airwave',
    '2005',
    'red',
    false
);


INSERT INTO hiring_candidates.driver_profiles(
    driver_license_expiration_date,
    driver_license_issue_date,
    driver_license_pd_id,
    event_key,
    executor_profile_id,
    first_name,
    last_name,
    park_id,
    phone_pd_id,
    providers,
    utc_created_at,
    utc_updated_at,
    work_status
) VALUES (
    '2027-11-01'::DATE,
    '2015-04-11'::DATE,
    'PRS-LICENSE-ID-MAX-161718',
    'eventid123',
    'exctrprfld321',
    'Ivan',
    'Danko',
    'smprk-id',
    'smphnpd-id',
    '{"smprvdrs", "smprvdrs"}',
    '2022-06-01T15:15:15'::TIMESTAMP,
    '2022-06-01T23:23:23'::TIMESTAMP,
    'ok'
);


INSERT INTO hiring_candidates.candidates(
    id,
    personal_phone_id,
    created_ts
) VALUES (
    'ABC123-CANDIDATE-MIN-ID',
    'JKL-PERSONAL-PHONE-789',
    '2022-06-01T05:00:00'::TIMESTAMP
), (
    'ABC123-CANDIDATE-MAX-ID',
    'ZAB-PERSONAL-PHONE-242526',
    '2022-06-01T05:00:00'::TIMESTAMP
);


INSERT INTO hiring_candidates.leads(
    activator_check,
    candidate_id,
    created_ts,
    external_id,
    is_deleted,
    is_rent,
    lead_id,
    service,
    updated_ts
) VALUES (
    'approved',
    'ABC123-CANDIDATE-MIN-ID',
    '2022-06-01T13:00:00'::TIMESTAMP,
    'DEF-EXTERNAL-ID-MIN-456',
    false,
    false,
    'GHI-LEAD-ID-MIN-789',
    'taxi',
    '2022-06-01T13:00:00'::TIMESTAMP
);


INSERT INTO hiring_candidates.leads(
    account_created_ts,
    account_id,
    activation_city,
    activation_park_db_id,
    activator_check,
    active_1,
    active_5,
    active_10,
    active_15,
    active_25,
    active_50,
    active_100,
    candidate_id,
    channel,
    created_ts,
    customer,
    date_of_birth,
    employment_type,
    external_id,
    extra,
    first_name,
    is_deleted,
    is_rent,
    last_name,
    lead_id,
    license_country,
    middle_name,
    park_condition_id,
    personal_license_id,
    personal_user_login_creator_id,
    profile_id,
    service,
    source_park_db_id,
    status,
    target_city,
    target_park_db_id,
    tariff,
    updated_ts,
    vacancy,
    workflow_type
) VALUES (
    '2022-06-01T01:00:00'::TIMESTAMP,
    'sOmE_aCcOuNt_Id',
    'Свердловск',
    'aCtIvAtIoN_pArK_dB_iD',
    'approved',
    '2022-06-01T02:00:00'::TIMESTAMP,
    '2022-06-01T03:00:00'::TIMESTAMP,
    '2022-06-01T04:00:00'::TIMESTAMP,
    '2022-06-01T05:00:00'::TIMESTAMP,
    '2022-06-01T06:00:00'::TIMESTAMP,
    '2022-06-01T07:00:00'::TIMESTAMP,
    '2022-06-01T08:00:00'::TIMESTAMP,
    'ABC123-CANDIDATE-MAX-ID',
    'freelance',
    '2022-06-01T09:00:00'::TIMESTAMP,
    'SoMe_CuStOmEr',
    '1991-10-04',
    'self_employed',
    'WXY-EXTERNAL-ID_MAX-222324',
    '{"courier_id": "SoMe_CoUrIeR_iD", "kiosk_session_id": "sOmE_kIoSk_SeSsIoN_iD"}',
    'Леонид',
    false,
    true,
    'Васечкин',
    'PRS-LEAD-ID-MAX-131415',
    'Камбоджа',
    'Владиленович',
    'SoMe_PaRk_CoNdItIoN_iD',
    'PRS-LICENSE-ID-MAX-161718',
    'TUV-CREATOR-LOGIN-ID-MAX-192021',
    'sOmE_pRoFiLe_Id',
    'taxi',
    'SoMe_SoUrCe_ParK_dB_iD',
    'Online training',
    '213',
    'sOmE_tArGeT_pArK_dB_iD',
    'comfort_plus',
    '2022-06-01T13:00:00'::TIMESTAMP,
    'Storekeeper',
    'CallCenterWithWeb'
);
