
INSERT INTO persey_labs.contacts
    (phone, email, web_site)
VALUES
    ('+79998887766', 'test_entity@yandex.ru', 'www.test_entity.ru');

INSERT INTO persey_labs.billing_infos
    (legal_name_short, legal_name_full, OGRN,
    legal_address, postal_address, web_license_resource,
    BIK, settlement_account, contract_start_dt, partner_uid)
VALUES
    ('test_entity_lab', 'test_entity_lab',
    'test_ogrn', 'test_address', 'test_address', 'www.test_license.com',
    'test_bik', 'test_account', 'test_date', 'test_uid');

INSERT INTO persey_labs.lab_entities
    (id, is_active, contacts, test_kind, employee_tests_threshold,
    custom_employee_address, custom_lab_id, contact_id,
    billing_info_id)
VALUES
    ('test_entity_lab_id', TRUE, 'test contacts', 'standart_covid_19', 10, TRUE, TRUE, 1, 1);
