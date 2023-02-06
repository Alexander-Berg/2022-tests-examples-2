INSERT INTO callcenter_qa.feedbacks
(id, created_at, yandex_uid, type, project, external_info, enabled_for_aggregation)
VALUES ('id1', '2020-07-19 11:13:59.00+0000', 'test_uid_1', 'ServerError', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}, "call_info": {"fcalled": "+71234567890", "queue": "disp_on_1", "metaqueue": "disp"}, "operator_info": {"callcenter": "test-callcenter"}}', true),
       ('id2', '2020-07-19 11:13:58.00+0000', 'test_uid_2', 'ServerError', 'call_center',
        '{"feedback_info": {"project": "test_project_2", "error_code": "500", "error_path": "test_error_path_2"}, "call_info": {"fcalled": "+71234567890", "queue": "disp_on_2", "metaqueue": "disp"}, "operator_info": {"callcenter": "test-callcenter"}}', true),
       ('id3', '2020-07-19 11:13:57.00+0000', 'test_uid_3', 'ServerError', 'call_center', NULL, false),
       ('id6', '2020-07-19 11:13:56.00+0000', 'test_uid_1', 'ServerError', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id4', '2020-07-19 11:13:55.00+0000', 'test_uid_4', 'ServerError', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id5', '2020-07-19 11:13:54.00+0000', 'test_uid_5', 'ServerError', 'call_center', NULL, true),
       ('id7', '2020-07-19 11:13:53.00+0000', 'test_uid_1', 'ServerError2', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id8', '2020-07-19 11:13:52.00+0000', 'test_uid_2', 'ServerError2', 'call_center',
        '{"feedback_info": {"project": "test_project_2", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id9', '2020-07-19 11:13:51.00+0000', 'test_uid_3', 'ServerError2', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id10', '2020-07-19 11:13:50.00+0000', 'test_uid_4', 'ServerError2', 'call_center',
        '{"feedback_info": {"project": "test_project_2", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id11', '2020-07-19 11:13:49.00+0000', 'test_uid_5', 'ServerError2', 'call_center', NUll, true),
       ('id12', '2020-07-19 11:13:51.00+0000', 'test_uid_6', 'ServerError3', 'call_center',
        '{"feedback_info": {"project": "test_project", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id13', '2020-07-19 11:13:51.00+0000', 'test_uid_7', 'ServerError3', 'call_center',
        '{"feedback_info": {"project": "test_project_2", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id14', '2020-07-19 11:13:51.00+0000', 'test_uid_8', 'ServerError3', 'call_center',
        '{"feedback_info": {"project": "test_project_3", "error_code": "500", "error_path": "test_error_path"}}', true),
       ('id15', '2020-07-19 11:13:51.00+0000', 'test_uid_9', 'ServerError3', 'call_center',
        '{"feedback_info": {"project": "test_project_4", "error_code": "500", "error_path": "test_error_path"}}', true);

INSERT INTO callcenter_qa.mass_incident_links
(ticket_id, feedback_id)
VALUES ('ticket_test_1', 'id3');

INSERT INTO callcenter_qa.tickets
(ticket_id, ticket_uri, ticket_name, feedback_id)
VALUES
('ticket_id1', 'CCINCIDENT_1', 'https://example.com/CCINCIDENT_1', 'id1'),
('ticket_id2', 'CCINCIDENT_2', 'https://example.com/CCINCIDENT_2', 'id2'),
('ticket_id3', 'CCINCIDENT_3', 'https://example.com/CCINCIDENT_3', 'id3'),
('ticket_id4', 'CCINCIDENT_4', 'https://example.com/CCINCIDENT_4', 'id4'),
('ticket_id7', 'CCINCIDENT_7', 'https://example.com/CCINCIDENT_7', 'id7'),
('ticket_id8', 'CCINCIDENT_8', 'https://example.com/CCINCIDENT_8', 'id8'),
('ticket_id9', 'CCINCIDENT_9', 'https://example.com/CCINCIDENT_9', 'id9'),
('ticket_id10', 'CCINCIDENT_10', 'https://example.com/CCINCIDENT_10', 'id10');
