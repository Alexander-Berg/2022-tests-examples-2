INSERT INTO callcenter_stats.general_call_history
(call_guid, project, init_event_id, initiator_type, initiator_id, initiated_at, finished_at, context)
VALUES
('20267ee994-1472736951-1653013025-0546323701', NULL, 1, 'ivr_flow_worker', 'taxi_order_by_phone_incoming_call', '2022-05-20 02:17:05+0000', '2022-05-20 02:17:06+0000', NULL),
('20267ee994-1712064041-1653053668-3140706214', NULL, 2, 'ivr_flow_worker', 'taxi_cc_sf_flow', '2022-05-20 13:34:28+0000', '2022-05-20 13:34:29+0000', NULL),
('202832a27f-2807725197-1653172759-0664680840', 'callcenter', 3, 'ivr_flow_worker', 'after_disp_call_flow' , '2022-05-21 22:39:19+0000', '2022-05-21 22:40:59+0000', '{"test1": "test", "test2": true, "test3": 8200}'),
('0000061102-2122152711-1653251073-0031560630', NULL, 4, 'abonent', 'phone_id_1', '2022-05-22 20:24:33+0000', '2022-05-22 20:25:09+0000', '{"prompt_url": "prompt1", "switch_to_csat": true}'),
('20267ee994-1690771271-1653011821-3611860272', 'callcenter', 5, 'ivr_flow_worker', 'after_disp_call_flow' , '2022-05-21 22:41:32+0000', '2022-05-21 22:41:23+0000', '{"test1": "test", "test2": false, "test3": 8201}');

INSERT INTO callcenter_stats.call_leg_history
(leg_id, call_guid, contact_type, contact_id, init_mode, initiated_at, answered_at, finished_at)
VALUES
('04b31aefcf26440086cdaf178f999055', '20267ee994-1472736951-1653013025-0546323701', 'abonent' , '4d0a60415e9f4650b2a1d6a3f55c3437', 'originate' , '2022-05-20 02:17:05+0000', NULL, '2022-05-20 02:17:06+0000'),
('d26bd5dde0ed4364bc884feacb31e455', '20267ee994-1712064041-1653053668-3140706214', 'abonent', '1c15ad4e7e934b29b70cc8217b3e9eb6', 'originate', '2022-05-20 13:34:28+0000', NULL, '2022-05-20 13:34:29+0000'),
('03eee1992ac54f569a399146d7f97d5c', '202832a27f-2807725197-1653172759-0664680840', 'abonent', '4d0a60415e9f4650b2a1d6a3f55c3437', 'originate', '2022-05-21 22:39:19+0000', NULL, '2022-05-21 22:40:59+0000'),
('2616fe1b-10c8-439a-baab-14d4cca66750', '0000061102-2122152711-1653251073-0031560630', 'abonent', 'phone_id_1', 'answer', '2022-05-22 20:24:33+0000', '2022-05-22 20:24:35+0000', '2022-05-22 20:25:09+0000'),
('40839be1881e420fb25e66dc55dc79f6', '20267ee994-1690771271-1653011821-3611860272', 'abonent', '4d0a60415e9f4650b2a1d6a3f55c3437', 'originate', '2022-05-21 22:41:32+0000', NULL, '2022-05-21 22:41:23+0000');

INSERT INTO callcenter_stats.call_event_history
(event_id, call_guid, leg_id, controller_id, event_type, event_time)
VALUES
(1, '20267ee994-1472736951-1653013025-0546323701', '04b31aefcf26440086cdaf178f999055', 'taxi_order_by_phone_incoming_call' , 'originate' , '2022-05-20 02:17:05+0000'),
(2, '20267ee994-1712064041-1653053668-3140706214', 'd26bd5dde0ed4364bc884feacb31e455', 'taxi_cc_sf_flow' , 'originate' , '2022-05-20 13:34:28+0000'),
(3, '202832a27f-2807725197-1653172759-0664680840', '03eee1992ac54f569a399146d7f97d5c', 'after_disp_call_flow' , 'originate' , '2022-05-21 22:39:19+0000'),
(4, '0000061102-2122152711-1653251073-0031560630', '2616fe1b-10c8-439a-baab-14d4cca66750', 'playback_flow' , 'answer' , '2022-05-22 20:24:33+0000'),
(5, '20267ee994-1690771271-1653011821-3611860272', '40839be1881e420fb25e66dc55dc79f6', 'after_disp_call_flow' , 'originate' , '2022-05-21 22:41:32+0000')
