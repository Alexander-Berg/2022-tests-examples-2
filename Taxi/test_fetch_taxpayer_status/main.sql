INSERT INTO se.taxpayer_status_cache
    (inn_pd_id, phone_pd_id, first_name, second_name,
     middle_name, registration_time, region_oktmo_code, oksm_code, activities)
VALUES
    ('ip1', 'pp1', 'F', 'L', 'M', '2022-06-12 12:00:00+03:00', '123456', '678', '[]'),
    ('ip2', 'pp2', 'F', 'L', 'M', '2022-06-12 12:00:00+03:00', '123456', null, null);

INSERT INTO se.nalogru_phone_bindings
    (inn_pd_id, phone_pd_id, status)
VALUES
    ('ip1', 'pp1', 'COMPLETED'),
    ('ip2', 'pp2', 'IN_PROGRESS'),
    ('ip3', 'pp3', 'COMPLETED');
